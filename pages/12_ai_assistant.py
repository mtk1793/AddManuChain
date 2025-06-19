import streamlit as st
import os
from src.components.ai_page_context import add_ai_page_context, get_ai_assistant_page_context
from src.components.universal_css import inject_universal_css

# Optional OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# Inject universal CSS styling
inject_universal_css()

# Hide the floating AI button on this page since this IS the AI assistant page
st.markdown("""
<style>
/* Hide floating AI button on this page */
# Hide floating AI button on this page */
#ai-float-btn {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Assistant")
st.write("Ask me anything about the dashboard, data, or get suggestions!")

# Initialize chat history
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []

# Configure OpenAI API with new client-based approach
client = None
if OPENAI_AVAILABLE:
    try:
        # Get API key from secrets or environment
        api_key = st.secrets.get("general", {}).get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.warning("OpenAI API key not found. AI assistant features are disabled. Please add OPENAI_API_KEY to .streamlit/secrets.toml")
        else:
            client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
else:
    st.warning("OpenAI library not installed. AI assistant features are disabled.")

# Chat interface
user_input = st.text_area(
    "Your question or request:", 
    key="ai_input", 
    placeholder="Ask about dashboard features, get suggestions, or request help...",
    height=100
)

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🚀 Ask AI", type="primary"):
        if user_input.strip():
            if not client:
                st.error("AI assistant is not available. Please configure OpenAI API key.")
                st.stop()
                
            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
            try:
                with st.spinner("🤖 AI is thinking..."):
                    context = """You are a helpful AI assistant for a MITACS 3D printing and supply chain dashboard. \
                    You help users with:\n- Dashboard navigation and features\n- Data analysis and insights\n- 3D printing processes and materials\n- Supply chain optimization\n- Quality assurance procedures\n- Inventory management\n- Device monitoring and maintenance\n- Certification processes\n\nProvide helpful, actionable suggestions and clear explanations."""
                    
                    # Using new API format
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": context},
                            {"role": "user", "content": user_input}
                        ],
                        max_tokens=512,
                        temperature=0.7
                    )
                    
                    ai_message = response.choices[0].message.content.strip()
                    st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_message})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.ai_chat_history = []
        st.rerun()

# Display chat history
if st.session_state.ai_chat_history:
    st.markdown("---")
    st.markdown("### 💬 Chat History")
    
    for i, msg in enumerate(reversed(st.session_state.ai_chat_history)):
        if msg["role"] == "user":
            with st.container():
                st.markdown(f"**👤 You:**")
                st.markdown(f"> {msg['content']}")
        else:
            with st.container():
                st.markdown(f"**🤖 AI Assistant:**")
                st.markdown(msg['content'])
        
        if i < len(st.session_state.ai_chat_history) - 1:
            st.markdown("---")

# Sidebar with quick suggestions
with st.sidebar:
    st.markdown("---")
    st.markdown("#### 💡 Quick Questions")
    
    suggestions = [
        "How do I add a new device?",
        "What materials are running low?",
        "Show me quality metrics",
        "How to improve efficiency?",
        "Explain dashboard features",
        "Help with inventory management"
    ]
    
    for suggestion in suggestions:
        if st.button(suggestion, key=f"suggestion_{suggestion}"):
            if not client:
                st.error("AI assistant is not available. Please configure OpenAI API key.")
                st.stop()
                
            st.session_state.ai_chat_history.append({"role": "user", "content": suggestion})
            try:
                with st.spinner("🤖 AI is thinking..."):
                    context = "You are a helpful AI assistant for a MITACS 3D printing and supply chain dashboard."
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": context},
                            {"role": "user", "content": suggestion}
                        ],
                        max_tokens=512,
                        temperature=0.7
                    )
                    ai_message = response.choices[0].message.content.strip()
                    st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_message})
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Add AI assistant context for this page (but don't render the floating assistant)
    add_ai_page_context(
        page_title="AI Assistant",
        page_type="tool",
        **get_ai_assistant_page_context()
    )
    
    st.markdown("---")