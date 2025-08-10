#!/usr/bin/env python3
"""
Simple cleanup system for in-memory ChromaDB storage
"""
import streamlit as st

def clear_chat_and_reset():
    """Clear chat messages and reset in-memory database"""
    print("💬 Clearing chat and resetting in-memory database...")
    
    # Clear chat messages
    st.session_state.messages = [
        st.session_state.messages[0]  # Keep the system message
    ]
    
    # Clear in-memory vector database (no file cleanup needed)
    st.session_state.vector_db = None
    st.session_state.documents_processed = False
    
    print("✅ Chat cleared and database reset")
    return True

def setup_session():
    """Setup session tracking (simplified for in-memory storage)"""
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
        print(f"🆔 New session: {st.session_state.session_id[:8]}...")
    
    # No cleanup needed for in-memory storage
    print("📝 Session setup complete (in-memory storage - no cleanup needed)")