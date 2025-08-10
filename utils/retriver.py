from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

def db_retriever(db, query):
    """
    Retrieve relevant documents from the in-memory vector database
    
    Args:
        db: ChromaDB instance (in-memory)
        query: User query string
        
    Returns:
        list: List of relevant document contents
    """
    try:
        print(f"🔍 db_retriever called with query: {query}")
        
        # Check if database instance exists
        if db is None:
            print(f"❌ No database instance provided")
            return []
        
        print(f"✅ Database instance exists: {type(db)}")
        
        # Create retriever with better search parameters
        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5
            }
        )
        
        print(f"🔧 Retriever created successfully")
        
        # Retrieve relevant documents
        relevant_docs = retriever.invoke(query)
        
        print(f"📊 Raw retrieval returned {len(relevant_docs)} documents")
        
        # Extract content and metadata
        results = []
        for i, doc in enumerate(relevant_docs, 1):
            content = doc.page_content.strip()
            print(f"Doc {i}: Content length = {len(content)}, Preview: {content[:50]}...")
            if content:  # Only add non-empty content
                results.append({
                    'content': content,
                    'metadata': doc.metadata,
                    'score': getattr(doc, 'score', 'N/A')
                })
        
        print(f"✅ Returning {len(results)} processed results")
        return results
        
    except Exception as e:
        print(f"❌ Error in retrieval: {str(e)}")
        import traceback
        traceback.print_exc()
        return []