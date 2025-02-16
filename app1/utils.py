from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os
from typing import List
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

class RAGManager:
    def __init__(self):
        self.qdrant_client = QdrantClient(":memory:")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="qwen-2.5-32b"
        )
        
        # Initialize Qdrant collection
        self.qdrant_client.create_collection(
            collection_name="documents",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name="documents",
            embedding=self.embeddings
        )

    def process_pdf(self, file_path: str):
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(docs)
        
        self.vector_store.add_documents(documents=splits)
        return len(splits)

    def get_qa_chain(self, session_id: str):
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        system_prompt = """You are a helpful assistant answering questions based on the provided documents.
        Use the following context to answer the question. If you don't know, say so.
        
        Context: {context}
        
        Chat History: {chat_history}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])

        retriever = self.vector_store.as_retriever()
        
        qa_chain = create_stuff_documents_chain(
            self.llm,
            prompt,
            document_variable_name="context",
        )

        chain = create_retrieval_chain(
            retriever,
            qa_chain,
        )

        return chain