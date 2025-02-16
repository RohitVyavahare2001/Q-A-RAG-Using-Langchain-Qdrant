from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from . import models, database
from .database import engine
from dotenv import load_dotenv
import shutil
from typing import Optional
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Initialize RAG components
qdrant_client = QdrantClient(":memory:")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize Qdrant collection
qdrant_client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="documents",
    embedding=embeddings
)

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="qwen-2.5-32b"
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Create temp directory
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/{file.filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(docs)
        
        # Add to vector store
        vector_store.add_documents(documents=splits)
        
        return {"message": "PDF processed successfully", "chunks": len(splits)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/chat/")
async def chat(
    request: ChatRequest,
    db: Session = Depends(database.get_db)
):
    try:
        # Get relevant documents
        retriever = vector_store.as_retriever()
        docs = retriever.get_relevant_documents(request.question)
        
        # Create context from documents
        context = "\n".join([doc.page_content for doc in docs])
        
        # Generate response using LLM
        messages = [
            {"role": "system", "content": f"Use this context to answer the question: {context}"},
            {"role": "user", "content": request.question}
        ]
        
        response = llm.invoke(messages)
        answer = response.content
        
        # Save to database
        chat_entry = models.ChatHistory(
            session_id=request.session_id,
            question=request.question,
            answer=answer
        )
        db.add(chat_entry)
        db.commit()
        
        return {
            "session_id": chat_entry.session_id,
            "answer": answer
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(database.get_db)
):
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.session_id == session_id
    ).all()
    return history

# Basic test route
@app.get("/")
def read_root():
    return {"Hello": "World"}