# RAG-Assistant
A RAG chatbot which can processes PDF files
# 🤖 RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built with Streamlit, LangChain, and Ollama. Upload PDF documents and ask questions about their content!

## ✨ Features

- **PDF Document Processing**: Upload and process multiple PDF files
- **Smart Text Chunking**: Intelligent document splitting for better retrieval
- **Vector Search**: Fast semantic search using ChromaDB and sentence transformers
- **RAG Integration**: Combines document retrieval with AI responses
- **Modern UI**: Clean, intuitive Streamlit interface
- **Chat History**: Persistent conversation memory

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Poetry** package manager installed
3. **Ollama** installed and running locally

### Installation

1. **Clone or download** this repository

2. **Download the Gemma3 model**:
   ```bash
   ollama pull gemma3:1b
   ```

3. **Upgrade Poetry**:
   ```bash
   pip install poetry --upgrade
   ```

4. **Install dependencies**:
   ```bash
   poetry install --no-root
   ```

5. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

6. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 📖 How to Use

### 1. Upload Documents
- Use the sidebar to upload one or more PDF files
- Click "Process Documents" to create embeddings
- Wait for the processing to complete

### 2. Ask Questions
- Type your questions in the chat interface
- bot will search through your documents and provide relevant answers
- You can ask general questions too (when no documents are uploaded)

### 3. Chat Features
- **Clear Chat**: Reset conversation history
- **Document Status**: See if documents are ready for querying
- **Real-time Processing**: Live feedback during document processing

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **LLM**: Ollama with Gemma3:1b model
- **Vector Database**: ChromaDB with inmemeory storage
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Text Processing**: Recursive character text splitting

### File Structure
```
RAG-Assistant
├── app.py          # Main Streamlit application 
├── utils
      ├── datastore.py  # Document processing and vector DB creation
      ├── retriver.py   # Document retrieval and search
      ├── memory_cleanup.py  # Delete created embeddings
├── pyproject.toml   # Python dependencies
└── README.md         # This file
```

### Key Components

#### `datastore.py`
- Handles PDF file uploads and processing
- Creates text chunks with optimal overlap
- Generates and stores embeddings in ChromaDB

#### `retriver.py`
- Performs semantic search on stored documents
- Returns relevant document chunks with metadata
- Includes similarity scoring and filtering

#### `app.py`
- Main Streamlit interface
- Manages chat flow and RAG integration
- Handles user interactions and responses

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check if gemma3:1b model is downloaded: `ollama list`

2. **PDF Processing Errors**
   - Verify PDF files are not corrupted
   - Check file permissions and size limits

3. **Memory Issues**
   - Large PDFs may require more RAM
   - Consider processing smaller documents first

4. **Dependency Issues**
   - Update pip: `pip install --upgrade pip`
   - Install dependencies individually if needed

### Performance Tips

- **Document Size**: Optimal chunk size is 1000 characters with 200 overlap
- **Model Selection**: Gemma3:1b provides good balance of speed and quality
- **Batch Processing**: Process multiple documents together for efficiency

## 🔒 Security Notes

- Documents are processed locally on your machine
- No data is sent to external services (except Ollama if using remote)
- Temporary files are automatically cleaned up

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this RAG chatbot!

---

**Happy Document Chatting! 📚💬** 
