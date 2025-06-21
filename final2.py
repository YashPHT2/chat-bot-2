import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from io import StringIO
import textwrap


GOOGLE_API_KEY = "" 

def page_setup():
    st.set_page_config(page_title="College Information Assistant", layout="wide")
    st.markdown("""
        <style>
        .stApp {
            background-color: #f0f0f5;
            color: #003366;
        }
        .stButton>button {
            background-color: #003366;
            color: #ffffff;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-size: 16px;
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
            border: 2px solid #003366;
        }
        .stButton>button:hover {
            background-color: #002244;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .stTextInput>div>input {
            border-radius: 5px;
            padding: 0.5rem;
            border: 2px solid #003366;
            transition: border-color 0.3s ease;
            width: 100%;
        }
        .stTextInput>div>input:focus {
            border-color: #002244;
        }
        .stMarkdown {
            font-family: 'Roboto', sans-serif;
        }
        .stProgress>div>div>div {
            background-color: #003366;
        }
        .stSidebar {
            background-color: #e0e0e0;
            padding: 20px;
            border-right: 2px solid #003366;
        }
        .stSidebar h2 {
            color: #003366;
        }
        .header-border {
            border-top: 2px solid #003366;
            padding-top: 10px;
            margin-top: 20px;
        }
        .input-container {
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
        }
        .input-container > button {
            margin-top: 10px;
            align-self: flex-end;
        }
        .chat-history, .contact-info {
            border: 1px solid #003366;
            border-radius: 5px;
            padding: 10px;
            background-color: #ffffff;
            margin-top: 20px;
        }
        .chat-item {
            border-bottom: 1px solid #e0e0e0;
            padding: 10px;
        }
        .chat-item:last-of-type {
            border-bottom: none;
        }
        .footer {
            margin-top: 20px;
            border-top: 2px solid #003366;
            padding: 10px 0;
            text-align: center;
        }
        .footer-button {
            background-color: #003366;
            color: #ffffff;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-size: 16px;
            transition: background-color 0.3s ease;
            border: none;
            cursor: pointer;
        }
        .footer-button:hover {
            background-color: #002244;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title("📚 College Information Assistant")
    st.markdown("<div class='header-border'></div>", unsafe_allow_html=True)
    st.markdown("### Upload your PDFs and ask questions about college information. Let's get started!")

def get_preset():
    st.sidebar.header("🎨 Preset Options")
    preset = st.sidebar.radio(
        "Select response style:",
        ("Formal", "Creative", "Concise"),
        index=0
    )
    st.sidebar.info("Select a style to tailor the AI responses to your preference.")
    return preset

def apply_preset(preset):
    presets = {
        "Creative": ("gemini-1.5-flash", 1.5, 0.95, 2500),
        "Concise": ("gemini-1.5-pro", 0.3, 0.8, 1000),
        "Formal": ("gemini-1.5-pro", 1.0, 0.94, 2000)
    }
    return presets.get(preset, presets["Formal"])

def process_pdfs(uploaded_files):
    progress_bar = st.progress(0)
    status_text = st.empty()
    combined_text = StringIO()

    for i, pdf in enumerate(uploaded_files):
        pdf_reader = PdfReader(pdf)
        status_text.text(f"Processing {pdf.name}...")

        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                combined_text.write(text)

        progress_bar.progress((i + 1) / len(uploaded_files))

    status_text.text("Processing complete!")
    return combined_text.getvalue()

def generate_answer(question, text, model, temperature, top_p, max_tokens):
    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "max_output_tokens": max_tokens,
        "response_mime_type": "text/plain",
    }
    model_instance = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config
    )
    response = model_instance.generate_content([question, text])
    return response.text

def main():
    page_setup()
    preset = get_preset()
    model, temperature, top_p, max_tokens = apply_preset(preset)

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    st.sidebar.header("")
    uploaded_files = st.file_uploader("Upload PDF files here", type='pdf', accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Processing PDFs..."):
            text = process_pdfs(uploaded_files)
        
        st.success("PDFs processed successfully. Ask your questions below.")

       
        with st.container():
            st.markdown("### Ask your question:")
            with st.form(key='question_form', clear_on_submit=True):
                question = st.text_input("Enter your question here:")
                submit_button = st.form_submit_button("Submit")
                if submit_button and question:
                    with st.spinner("Generating answer..."):
                        answer = generate_answer(question, text, model, temperature, top_p, max_tokens)
                    st.session_state['history'].append((question, answer))

        
        st.subheader("ANSWERS")
        chat_container = st.container()
        with chat_container:
            if st.session_state['history']:
                with st.expander("View ANSWERS"):
                    for q, a in st.session_state['history']:
                        st.markdown(f"<div class='chat-item'><strong>You:</strong> {q}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='chat-item'><strong>Assistant:</strong> {textwrap.fill(a, width=100)}</div>", unsafe_allow_html=True)

        
        with st.expander("Contact Us"):
            st.markdown("""
                <div class='contact-info'>
                    <p><strong>Mobile No.:</strong> 9811XXXXX</p>
                    <p><strong>Email:</strong> <a href='mailto:gh@gmail.com'>gh@gmail.com</a></p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == '__main__':
    genai.configure(api_key="")
    main()


