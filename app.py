import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from utils.datastore import db_init
from utils.retriver import db_retriever
from utils.memory_cleanup import clear_chat_and_reset, setup_session
import os

# Page configuration
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are Sara, a helpful AI Assistant born in Korea. You help users with questions about their uploaded documents.")
    ]
    st.session_state.vector_db = None  # Store in-memory database
    st.session_state.documents_processed = False

# Setup session (simplified for in-memory storage)
setup_session()

# Initialize Ollama model
try:
    model = ChatOllama(model="gemma3:1b")
    st.success("✅ Ollama model loaded successfully!")
except Exception as e:
    st.error(f"❌ Failed to load Ollama model: {str(e)}")
    st.info("Please make sure Ollama is running and the model is available")
    st.stop()

def get_model_response(query):
    """Get response from the language model"""
    try:
        with st.spinner("🤔 Assistant is thinking..."):
            # Convert string query to HumanMessage for proper model input
            if isinstance(query, str):
                messages = [HumanMessage(content=query)]
            else:
                messages = query
            result = model.invoke(messages)
        return result.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def process_rag_query(query, vector_db):
    """Process RAG query with document retrieval"""
    try:
        print(f"🔍 Processing RAG query: {query}")
        print(f"📊 Vector DB exists: {vector_db is not None}")
        
        # Check if user is asking about a specific document
        specific_doc_filter = None
        query_lower = query.lower()
        
        # Look for patterns like "in document X" or "from file Y"
        import re
        doc_patterns = [
            r'in (?:document|file|pdf) ["\']?([^"\']+?)["\']?(?:\s|$)',
            r'from (?:document|file|pdf) ["\']?([^"\']+?)["\']?(?:\s|$)',
            r'according to ["\']?([^"\']+?)["\']?(?:\s|$)'
        ]
        
        for pattern in doc_patterns:
            match = re.search(pattern, query_lower)
            if match:
                specific_doc_filter = match.group(1).strip()
                print(f"🎯 User asking about specific document: {specific_doc_filter}")
                break
        
        with st.spinner("🔍 Searching through documents..."):
            relevant_docs = db_retriever(db=vector_db, query=query)
        
        # Filter by specific document if requested
        if specific_doc_filter:
            filtered_docs = []
            for doc in relevant_docs:
                doc_name = doc.get('metadata', {}).get('document_name', '').lower()
                source_doc = doc.get('metadata', {}).get('source_document', '').lower()
                if (specific_doc_filter in doc_name or 
                    specific_doc_filter in source_doc or
                    doc_name in specific_doc_filter or
                    source_doc in specific_doc_filter):
                    filtered_docs.append(doc)
            
            if filtered_docs:
                relevant_docs = filtered_docs
                print(f"🎯 Filtered to {len(relevant_docs)} documents matching '{specific_doc_filter}'")
            else:
                return f"I couldn't find any information about '{specific_doc_filter}' in your uploaded documents. Please check the document name and try again."
        
        print(f"📄 Found {len(relevant_docs)} relevant documents")
        
        if not relevant_docs:
            return "I couldn't find any relevant information in your documents for this query. Please try rephrasing your question."
        
        # Debug: Show what documents were found
        for i, doc in enumerate(relevant_docs[:3]):
            source_name = doc.get('metadata', {}).get('document_name', f'Doc {i+1}')
            print(f"Doc {i+1} ({source_name}): {doc['content'][:100]}...")
        
        # Format the context for the model with document sources
        context_parts = []
        for i, doc in enumerate(relevant_docs[:3]):
            source_name = doc.get('metadata', {}).get('document_name', f'Document {i+1}')
            page_num = doc.get('metadata', {}).get('page', 'Unknown')
            context_parts.append(f"[Source: {source_name}, Page: {page_num}]\n{doc['content']}")
        
        context = "\n\n".join(context_parts)
        print(f"📝 Context length: {len(context)} characters")
        
        # Create enhanced prompt
        enhanced_prompt = f"""Based on the following relevant information from your documents, please answer the user's question:

Context:
{context}

User Question: {query}

Please provide an accurate response based on the exact content from the retrieved documents. When referencing information, mention which document it comes from (e.g., "According to [document name]...")."""
        
        print(f"🚀 Sending enhanced prompt to model (length: {len(enhanced_prompt)} chars)")
        return get_model_response(enhanced_prompt)
        
    except Exception as e:
        print(f"❌ Error in process_rag_query: {str(e)}")
        return f"Error processing RAG query: {str(e)}"

# Main UI
st.title("🤖 RAG AI Assistant")
st.markdown("Upload PDF documents and ask questions about them!")

# Sidebar for document upload
with st.sidebar:
    st.header("📚 Document Upload")
    
    uploaded_files = st.file_uploader(
        label="Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="doc_upload",
        help="Select one or more PDF files to analyze"
    )
    
    if uploaded_files:
        st.success(f"📄 {len(uploaded_files)} file(s) selected")
        
        if st.button("🚀 Process Documents", type="primary"):
            try:
                with st.spinner("🔄 Processing documents..."):
                    vector_db = db_init(uploaded_files)
                    st.session_state.vector_db = vector_db
                    st.session_state.documents_processed = True
                st.success("✅ Documents processed successfully in memory!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error processing documents: {str(e)}")
    
    # Show processing status
    if st.session_state.documents_processed:
        st.success("✅ Documents are ready for querying!")
        
        # Show loaded documents
        if st.session_state.vector_db:
            st.subheader("📋 Loaded Documents")
            try:
                # Get a sample of documents to show what's loaded
                sample_docs = st.session_state.vector_db.similarity_search("", k=10)
                doc_names = set()
                for doc in sample_docs:
                    if doc.metadata and 'document_name' in doc.metadata:
                        doc_names.add(doc.metadata['document_name'])
                
                if doc_names:
                    for doc_name in sorted(doc_names):
                        st.write(f"• {doc_name}")
                    
                    st.info("💡 You can ask questions about specific documents by saying 'in document [name]' or 'from file [name]'")
                else:
                    st.write("Documents loaded (names not available)")
            except Exception as e:
                st.write("Documents loaded successfully")
    else:
        st.info("📤 Please upload and process documents first")
    


# Main chat interface
st.header("💬 Chat with AI-Assistant")

# Display chat messages
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Chat input
if prompt := st.chat_input("Ask me anything about your documents..."):
    # Add user message
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        if st.session_state.documents_processed and st.session_state.vector_db:
            # Use RAG for document-related queries
            response = process_rag_query(prompt, st.session_state.vector_db)
        else:
            # Regular chat response
            response = get_model_response(prompt)
        
        st.markdown(response)
        st.session_state.messages.append(AIMessage(content=response))

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Upload PDF documents first, then ask questions about their content!")

# Clear chat button
if st.button("🗑️ Clear Chat"):
    # Clear chat and reset in-memory database
    clear_chat_and_reset()
    st.success("✅ Chat cleared and database reset!")
    st.rerun()