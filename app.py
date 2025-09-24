import streamlit as st
import openai
from datetime import datetime
import base64
from PIL import Image
import PyPDF2
import io

# Page configuration
st.set_page_config(
    page_title="GP Consultants",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .advisor-selector {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">GP Consultants</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #666; margin-bottom: 2rem;">Professional AI Consultation Platform</h3>', unsafe_allow_html=True)

# Sidebar for API key and advisor selection
with st.sidebar:
    st.title("Configuration")

    # OpenAI API Key
    api_key = st.text_input("OpenAI API Key", type="password",
                           help="Get your API key from https://platform.openai.com/")

    st.markdown("---")

    # Advisor personality selection
    st.title("Choose Your Consultant")
    advisor_type = st.selectbox(
        "Select consultant expertise:",
        ["Venture Capitalist", "Tech Expert", "Marketing Guru", "Financial Advisor"]
    )

    # Advisor descriptions
    advisor_info = {
        "Venture Capitalist": "Focuses on scalability, market size, and funding strategies",
        "Tech Expert": "Provides technical insights and development guidance",
        "Marketing Guru": "Specializes in customer acquisition and brand building",
        "Financial Advisor": "Offers financial planning and business model advice"
    }

    st.info(advisor_info[advisor_type])

    st.markdown("---")

    # File upload section
    st.title("Document Analysis")
    uploaded_file = st.file_uploader(
        "Upload document for analysis",
        type=['pdf', 'txt', 'png', 'jpg', 'jpeg'],
        help="Upload business documents, images, or PDFs for consultant analysis"
    )

    st.markdown("---")
    st.markdown("### Platform Features")
    st.markdown("- Real-time AI consultation")
    st.markdown("- Multiple expert personalities")
    st.markdown("- Document and image analysis")
    st.markdown("- Conversation memory")
    st.markdown("- Business-focused insights")

# Helper function to process uploaded files
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.type

        if file_type == "text/plain":
            # Process text file
            content = str(uploaded_file.read(), "utf-8")
            return f"TEXT DOCUMENT CONTENT:\n{content}"

        elif file_type == "application/pdf":
            # Process PDF file
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return f"PDF DOCUMENT CONTENT:\n{text}"
            except Exception as e:
                return f"Error reading PDF: {str(e)}"

        elif file_type.startswith("image/"):
            # Process image file
            try:
                image = Image.open(uploaded_file)
                # Convert image to base64 for analysis
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return f"IMAGE UPLOADED: {uploaded_file.name}\nImage has been processed and is ready for analysis. Please describe what you'd like me to analyze about this image."
            except Exception as e:
                return f"Error processing image: {str(e)}"

    return None

# Main chat interface
if api_key:
    # Set OpenAI API key
    openai.api_key = api_key

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Process uploaded file if exists
    file_content = process_uploaded_file(uploaded_file) if uploaded_file else None

    # Advisor system prompts
    system_prompts = {
        "Venture Capitalist": """You are an experienced venture capitalist with 15+ years in Silicon Valley.
        You focus on scalability, market opportunity, competitive advantages, and funding strategies.
        Give direct, actionable advice with specific metrics and examples. Be encouraging but realistic.""",

        "Tech Expert": """You are a senior technical advisor who has built multiple successful tech products.
        You understand architecture, development processes, and technical challenges.
        Provide practical technical guidance and help prioritize features. Focus on MVP and iterative development.""",

        "Marketing Guru": """You are a marketing expert who has grown multiple companies from 0 to millions of users.
        You specialize in customer acquisition, brand building, and growth strategies.
        Give actionable marketing advice with specific tactics and channels.""",

        "Financial Advisor": """You are a business financial advisor specializing in startups and SMBs.
        You help with business models, pricing strategies, cash flow, and financial planning.
        Provide clear financial guidance with practical examples."""
    }

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Display file upload status
    if file_content and uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        if st.button("Analyze Uploaded Document"):
            analysis_prompt = f"Please analyze this document from your perspective as a {advisor_type}:\n\n{file_content}"
            st.session_state.messages.append({"role": "user", "content": f"Document Analysis Request: {uploaded_file.name}"})

    # Chat input
    if prompt := st.chat_input(f"Ask your {advisor_type.lower()} anything about your business..."):
        # Combine user prompt with file content if available
        full_prompt = prompt
        if file_content:
            full_prompt = f"{prompt}\n\nRELEVANT DOCUMENT:\n{file_content}"

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner(f"Your {advisor_type.lower()} is analyzing..."):
                try:
                    # Prepare messages for OpenAI
                    messages = [
                        {"role": "system", "content": system_prompts[advisor_type]}
                    ]

                    # Add conversation history (last 8 messages to stay within limits)
                    recent_messages = st.session_state.messages[-8:]
                    for msg in recent_messages[:-1]:  # Exclude the current message
                        messages.append({"role": msg["role"], "content": msg["content"]})

                    # Add current message with file content
                    messages.append({"role": "user", "content": full_prompt})

                    # Call OpenAI API
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=800,
                        temperature=0.7
                    )

                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Please check your API key and try again.")

else:
    # Welcome screen when no API key
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 🚀 Welcome to AI Business Advisor!

        **Get expert business advice powered by AI**

        #### 🎯 What you can do:
        - Get funding strategy advice from a VC perspective
        - Receive technical guidance for your product
        - Learn marketing tactics to grow your business
        - Plan your finances and business model

        #### 🔧 To get started:
        1. Add your OpenAI API key in the sidebar
        2. Choose your preferred advisor type
        3. Start asking business questions!

        #### 💡 Example questions:
        - "How should I price my SaaS product?"
        - "What's the best go-to-market strategy for a B2B tool?"
        - "How do I validate my business idea?"
        - "What metrics should I track for my startup?"
        """)

        st.info("💡 **Tip**: Get your free OpenAI API key at https://platform.openai.com/")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with Streamlit & OpenAI | Perfect for entrepreneurs and business owners"
    "</div>",
    unsafe_allow_html=True
)