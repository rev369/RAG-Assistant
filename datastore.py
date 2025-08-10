from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import os
import tempfile
import shutil

def db_init(uploaded_files):
    """
    Initialize vector database with uploaded PDF files in memory (session storage)
    
    Args:
        uploaded_files: List of uploaded file objects from Streamlit
        
    Returns:
        Chroma: In-memory ChromaDB instance
    """
    # No need for persistent folder - using in-memory storage
    
    all_documents = []
    
    # Process each uploaded PDF file
    for uploaded_file in uploaded_files:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Load PDF content
            loader = PyMuPDFLoader(tmp_file_path)
            documents = loader.load()
            
            # Add document name to metadata for each page
            for doc in documents:
                if not hasattr(doc, 'metadata') or doc.metadata is None:
                    doc.metadata = {}
                doc.metadata['source_document'] = uploaded_file.name
                doc.metadata['document_name'] = uploaded_file.name.replace('.pdf', '')
            
            all_documents.extend(documents)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            print(f"✅ Processed {uploaded_file.name}: {len(documents)} pages")
            
        except Exception as e:
            print(f"Error processing {uploaded_file.name}: {str(e)}")
            continue
    
    if not all_documents:
        raise ValueError("No documents were successfully loaded")
    
    print(f"----------{len(all_documents)} documents loaded----------")
    
    # Improved text splitting with better parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    docs = text_splitter.split_documents(all_documents)
    print(f"----------{len(docs)} chunks created----------")
    
    # Create embeddings
    embedding_func = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # Create in-memory vector database (no persistence)
    db = Chroma.from_documents(
        documents=docs,
        embedding=embedding_func
        # No persist_directory = in-memory storage
    )
    
    print("----------embeddings created in memory (session storage)----------")
    
    # Debug: Test the database
    try:
        test_results = db.similarity_search("test", k=1)
        print(f"🧪 Database test: Found {len(test_results)} documents")
        if test_results:
            print(f"🧪 Sample content: {test_results[0].page_content[:100]}...")
    except Exception as e:
        print(f"⚠️ Database test failed: {e}")
    
    return db
