import streamlit as st
from openai import OpenAI
import os
import json

def get_openai_client():
    """Initialize OpenAI client with API key from secrets or environment"""
    try:
        # Try to get API key from secrets first, then environment
        api_key = st.secrets.get("general", {}).get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not found. Please add it to .streamlit/secrets.toml")
            return None
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        return None

def extract_page_context():
    """Extract context from the current page content"""
    context_data = {
        "page_title": "Dashboard",
        "visible_elements": [],
        "metrics": [],
        "charts": [],
        "tables": []
    }
    
    # Try to extract information from session state
    if hasattr(st.session_state, 'username'):
        context_data["user"] = st.session_state.username
    
    # Get current page from URL or session state
    try:
        # This is a simplified context extraction
        # In a real implementation, you might want to pass specific page data
        if "current_page_data" in st.session_state:
            context_data.update(st.session_state.current_page_data)
    except:
        pass
    
    return context_data

def generate_ai_response(user_input, page_context):
    """Generate AI response with page context"""
    client = get_openai_client()
    if not client:
        return "Sorry, I'm unable to process your request right now. Please check the API configuration."
    
    try:
        # Create context-aware system prompt
        system_prompt = f"""You are a helpful AI assistant for the MITACS 3D printing and supply chain dashboard. 
        
Current page context: {json.dumps(page_context, indent=2)}

You help users with:
- Dashboard navigation and features
- Data analysis and insights from the current page
- 3D printing processes and materials
- Supply chain optimization
- Quality assurance procedures
- Inventory management
- Device monitoring and maintenance
- Certification processes

Provide helpful, actionable suggestions based on both the user's question and the current page context. 
If the user asks about something visible on the current page, reference it specifically.
Keep responses concise but informative."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=512,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def render_floating_ai_assistant():
    """Render the floating AI assistant with popover interface"""
    
    # Initialize chat history in session state
    if "floating_ai_chat_history" not in st.session_state:
        st.session_state.floating_ai_chat_history = []
    
    # Get current page context
    page_context = extract_page_context()
    
    # Generate unique keys based on page title and session
    import time
    import hashlib
    import uuid
    
    # Get the current script name or page identifier
    try:
        # Get the current file name from Streamlit's context
        current_script = st.runtime.scriptrunner.script_runner.get_script_run_ctx().session_info.script or "unknown"
        script_name = current_script.split('/')[-1].replace('.py', '') if current_script else "unknown"
    except:
        script_name = "unknown"
    
    # Create a more unique page key using script name, page title, and session info
    base_key = f"{script_name}_{page_context.get('page_title', 'default')}".lower().replace(" ", "_").replace("/", "_")
    
    # Add session-specific identifier and timestamp to ensure uniqueness across reruns
    if 'ai_session_id' not in st.session_state:
        st.session_state.ai_session_id = str(uuid.uuid4())[:8]
    
    # Use a more stable key generation to avoid conflicts
    page_key = f"{base_key}_{st.session_state.ai_session_id}"
    
    # Add a render counter to prevent duplicate renders
    render_key = f"ai_assistant_rendered_{page_key}"
    if render_key in st.session_state:
        return  # Already rendered for this page/session combo
    st.session_state[render_key] = True
    
    # Create the floating button with popover
    with st.popover("🤖 AI Assistant", use_container_width=False, help="Ask me anything about this page or the dashboard!"):
        st.markdown("### 🤖 AI Assistant")
        
        # Show page context info
        if page_context.get("page_title"):
            st.info(f"📍 Currently on: **{page_context['page_title']}**")
        
        # Display chat history in a more compact way
        if st.session_state.floating_ai_chat_history:
            st.markdown("**💬 Recent Conversation:**")
            
            # Create a scrollable container for chat history
            chat_container = st.container()
            with chat_container:
                # Show only last 3 exchanges (6 messages) to keep it manageable
                recent_messages = st.session_state.floating_ai_chat_history[-6:]
                
                for i, msg in enumerate(recent_messages):
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style='background: #e3f2fd; border-radius: 10px; padding: 8px 12px; margin: 5px 0; margin-left: 20px; border-left: 3px solid #2196f3; font-size: 0.9em;'>
                        <strong>👤 You:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background: #f3e5f5; border-radius: 10px; padding: 8px 12px; margin: 5px 0; margin-right: 20px; border-left: 3px solid #9c27b0; font-size: 0.9em;'>
                        <strong>🤖 AI:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
            
            st.divider()
        
        # Input for new question
        user_input = st.text_area(
            "Ask me anything:",
            placeholder="e.g., 'What can I do on this page?', 'Explain the data shown', 'How to add a new device?'",
            height=80,
            key=f"floating_ai_input_{page_key}",
            help="I can help you understand this page, navigate the dashboard, or answer questions about your data."
        )
        
        # Buttons row
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ask_button = st.button("💬 Ask AI", type="primary", key=f"floating_ai_ask_{page_key}", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", key=f"floating_ai_clear_{page_key}", use_container_width=True)
        with col3:
            if len(st.session_state.floating_ai_chat_history) > 0:
                if st.button("📖 History", key=f"floating_ai_history_{page_key}", use_container_width=True):
                    # Show full history in an expander
                    with st.expander("Full Chat History", expanded=True):
                        for msg in st.session_state.floating_ai_chat_history:
                            if msg["role"] == "user":
                                st.markdown(f"**👤 You:** {msg['content']}")
                            else:
                                st.markdown(f"**🤖 AI:** {msg['content']}")
                        st.button("Close History", key=f"close_history_{page_key}")
        
        # Handle ask button click
        if ask_button and user_input.strip():
            # Add user message
            st.session_state.floating_ai_chat_history.append({
                "role": "user", 
                "content": user_input.strip()
            })
            
            # Generate AI response
            with st.spinner("🤖 AI is thinking..."):
                ai_response = generate_ai_response(user_input.strip(), page_context)
                st.session_state.floating_ai_chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
            
            st.rerun()
        
        # Handle clear button click
        if clear_button:
            st.session_state.floating_ai_chat_history = []
            st.rerun()
        
        st.divider()
        
        # Quick suggestions based on current page
        st.markdown("**⚡ Quick Questions:**")
        
        # Page-specific suggestions
        page_type = page_context.get("page_type", "general")
        
        if page_type == "dashboard":
            suggestions = [
                "Explain the key metrics",
                "What trends do you see?",
                "How can I improve performance?",
                "Show me important alerts",
                "Guide me through this dashboard"
            ]
        elif page_type == "management":
            suggestions = [
                "How do I add a new item?",
                "What can I do on this page?",
                "Show me filtering options",
                "Explain the data columns",
                "How to export this data?"
            ]
        else:
            suggestions = [
                "What is this page for?",
                "How do I navigate here?",
                "Show me the main features",
                "Help me get started",
                "Explain this interface"
            ]
        
        # Create a more compact grid for suggestions
        num_suggestions = len(suggestions)
        cols = st.columns(2)
        for idx, suggestion in enumerate(suggestions):
            # Use a simpler but unique key for each button
            suggestion_key = f"floating_suggestion_{page_key}_{idx}"
            with cols[idx % 2]:
                if st.button(suggestion, key=suggestion_key):
                    # Add suggestion as user message
                    st.session_state.floating_ai_chat_history.append({
                        "role": "user",
                        "content": suggestion
                    })
                    # Generate AI response
                    with st.spinner("🤖 Analyzing..."):
                        ai_response = generate_ai_response(suggestion, page_context)
                        st.session_state.floating_ai_chat_history.append({
                            "role": "assistant",
                            "content": ai_response
                        })
                    st.rerun()
        
        # Add footer with tips
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
        💡 <strong>Tip:</strong> I can see what's on this page and help you understand the data, navigate features, or answer questions!
        </div>
        """, unsafe_allow_html=True)
