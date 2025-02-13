import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Query
from rag_pipeline import load_and_split, store_vectors
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from qdrant_client import QdrantClient

load_dotenv()
llm = ChatGroq(model="qwen-2.5-32b")
retriever = QdrantClient(url="http://localhost:6333")
conversation_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever)
chat_history = []

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with open(file.filename, "wb") as f:
        f.write(await file.read())
    docs = load_and_split(file.filename)
    store_vectors(docs)
    return {"message": "Vectors stored successfully."}

@app.post("/chat/")
async def chat(query: str = Query(...)):
    global chat_history
    response = conversation_chain.run({"question": query, "chat_history": chat_history})
    chat_history.append((query, response))
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)