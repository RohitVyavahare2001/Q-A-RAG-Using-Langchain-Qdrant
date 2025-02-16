# RAG-Based Document Q&A System

A powerful document question-answering system built with RAG (Retrieval Augmented Generation) architecture, allowing users to upload PDFs and engage in intelligent conversations about their content.

## 🚀 Features

- 📄 PDF document upload and processing
- 💬 Interactive chat interface
- 🔍 Semantic search capabilities
- 🧠 Context-aware responses using RAG
- 💾 Persistent chat history
- 🔄 Session management
- 📊 Debug information panel

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Database**: MySQL
- **LLM**: Groq (qwen-2.5-32b)
- **Vector Store**: Qdrant
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Document Processing**: LangChain

## 📋 Prerequisites

- Python 3.8+
- MySQL database
- Groq API key
- Git

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rag-document-qa.git
cd rag-document-qa
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` file with your credentials:
```
groq_api_key = "your_groq_api_key"
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/database_name"
```

5. Create MySQL database:
```sql
CREATE DATABASE rag_db;
```

## 🚀 Running the Application

1. Start the FastAPI backend:
```bash
uvicorn app1.main:app --reload
```

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run app1/app.py
```

3. Open your browser and navigate to:
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
app1/
├── main.py         # FastAPI backend
├── app.py          # Streamlit frontend
├── models.py       # Database models
├── database.py     # Database configuration
├── utils.py        # RAG utilities
└── __init__.py
```

## 🔧 Usage

1. Upload a PDF document using the sidebar
2. Wait for the document to be processed
3. Start asking questions about the document content
4. View chat history and debug information as needed

## 🌟 Key Features Explained

### Document Processing
- Splits documents into manageable chunks
- Generates vector embeddings
- Stores in Qdrant vector database

### Question Answering
- Retrieves relevant context using semantic search
- Generates accurate responses using Groq LLM
- Maintains conversation context

### Data Persistence
- Stores chat history in MySQL
- Maintains session information
- Enables conversation retrieval

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details

## 📧 Contact

Email - rohitvyavahare2001@gmail.com
Linkedin - https://www.linkedin.com/in/rohitvyavahare2001/
