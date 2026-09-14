import os
import json
import time
from typing import Optional, Dict, Any
import streamlit as st
from pypdf import PdfReader
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="LexiClear | AI Legal Copilot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling & High-Contrast Visual Standards
st.markdown("""
    <style>
    .metric-card {
        background-color: #1a1c24;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .disclaimer-box {
        background-color: #1e1e2f;
        border-left: 4px solid #6366f1;
        padding: 14px;
        border-radius: 4px;
        font-size: 0.90rem;
        color: #f1f5f9;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# Resilient API Call with Multi-Model Fallback
def generate_with_fallback(client: genai.Client, contents: Any, config: Optional[types.GenerateContentConfig] = None) -> Any:
    """
    Executes a resilient model call by cascading across multiple Gemini models
    with automated retry logic to manage concurrency spikes and 503 limits.
    """
    candidate_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]
    last_error = None

    for model_name in candidate_models:
        for attempt in range(2):
            try:
                if config:
                    return client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config
                    )
                else:
                    return client.models.generate_content(
                        model=model_name,
                        contents=contents
                    )
            except Exception as e:
                last_error = e
                time.sleep(1)
                continue

    raise last_error

# High-Performance Cached PDF Extractor
@st.cache_data(show_spinner=False)
def extract_pdf_text(uploaded_file) -> Optional[str]:
    """
    Extracts and caches clean raw text from uploaded PDF document for optimal performance.
    """
    if uploaded_file is None:
        return None
    try:
        reader = PdfReader(uploaded_file)
        extracted_text = []
        for page in reader.pages:
            content = page.extract_text()
            if content:
                extracted_text.append(content)
        full_text = "\n".join(extracted_text).strip()
        return full_text if full_text else None
    except Exception as e:
        st.error(f"Error parsing PDF content: {e}")
        return None

# Structured Document Analysis Engine
def analyze_legal_document(client: genai.Client, doc_text: str) -> Dict[str, Any]:
    """
    Analyzes legal text with strict JSON schema adherence and bounded temperature.
    """
    system_prompt = (
        "You are an expert legal assistant AI designed to simplify contracts and legal agreements for everyday users. "
        "Analyze the provided document and return a strictly valid JSON object conforming to the following schema:\n"
        "{\n"
        '  "doc_type": "Agreement type (e.g., Employment, NDA, Lease, Freelance, Service Agreement)",\n'
        '  "overall_risk_level": "Low" | "Medium" | "High",\n'
        '  "summary": "Concise summary in plain layman English (3-4 sentences)",\n'
        '  "key_obligations": ["List of core obligations/rules the user must follow"],\n'
        '  "red_flags": [\n'
        '      {"clause_name": "...", "severity": "High" | "Medium" | "Low", "concern": "Why this is risky in plain terms", "recommendation": "What to ask or negotiate"}\n'
        '  ],\n'
        '  "lawyer_checklist": ["Specific, pointed questions to ask a lawyer before signing"]\n'
        "}\n"
        "Ground all findings strictly on the document text. Do not invent details. Output ONLY raw JSON."
    )

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        temperature=0.2
    )
    
    response = generate_with_fallback(client, contents=[doc_text], config=config)
    return json.loads(response.text)

# Sidebar Configuration
with st.sidebar:
    st.title("⚖️ LexiClear")
    st.caption("AI-Powered Legal Document Auditor & Simplifier")
    st.divider()
    
    api_key = st.text_input(
        label="Gemini API Key",
        type="password",
        help="Enter your Google AI Studio API key (Required for secure document auditing)",
        placeholder="AIzaSy...",
        label_visibility="visible"
    )
    st.markdown("Get your key free at [Google AI Studio](https://aistudio.google.com/).")
    
    st.divider()
    st.markdown("### Submission Highlights")
    st.markdown("✅ **Zero-Jargon Simplification**")
    st.markdown("✅ **Automated Risk & Clause Radar**")
    st.markdown("✅ **Grounded Interactive Q&A**")
    st.markdown("✅ **Pre-Signing Lawyer Checklist**")

# Main Dashboard Interface
st.title("Automated Legal Assistance & Risk Radar")
st.markdown(
    """
    <div class="disclaimer-box" role="alert" aria-label="Legal Notice">
        <strong>⚠️ Legal Information Notice:</strong> This tool uses GenAI to assist and summarize legal documents. 
        It does not provide formal legal advice or substitute an authorized legal professional.
    </div>
    """,
    unsafe_allow_html=True
)

if not api_key:
    st.info("👈 Please enter your Gemini API Key in the sidebar to activate the analysis engine.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# Accessible File Uploader
uploaded_file = st.file_uploader(
    label="Upload Legal Document (PDF or TXT format)",
    type=["pdf", "txt"],
    help="Upload your employment contract, NDA, or service agreement for GenAI risk auditing",
    label_visibility="visible"
)

if uploaded_file:
    if "doc_text" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
        with st.spinner("Parsing and caching document content..."):
            if uploaded_file.type == "application/pdf":
                doc_text = extract_pdf_text(uploaded_file)
            else:
                doc_text = uploaded_file.read().decode("utf-8")
            
            st.session_state.doc_text = doc_text
            st.session_state.file_name = uploaded_file.name
            st.session_state.analysis = None
            st.session_state.chat_history = []

    doc_text = st.session_state.doc_text

    if not doc_text:
        st.error("Could not extract readable text from this document. Please ensure it is a text-based document.")
        st.stop()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"📄 Document Loaded: **{uploaded_file.name}** (~{len(doc_text.split())} words)")
    with col2:
        start_analysis = st.button(
            label="🚀 Analyze Document",
            type="primary",
            use_container_width=True,
            help="Trigger AI risk analysis, clause scoring, and negotiation checklist generation"
        )

    if start_analysis or st.session_state.analysis is not None:
        if st.session_state.analysis is None:
            with st.spinner("Analyzing clauses, evaluating liabilities, and computing risk ratings..."):
                try:
                    analysis_result = analyze_legal_document(client, doc_text)
                    st.session_state.analysis = analysis_result
                except Exception as e:
                    st.error(f"Analysis pipeline error: {e}")
                    st.stop()

        analysis = st.session_state.analysis

        # High-Level Metrics
        st.divider()
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Detected Document Type", analysis.get("doc_type", "General Agreement"))
        with m_col2:
            st.metric("Overall Risk Score", analysis.get("overall_risk_level", "Medium"))
        with m_col3:
            st.metric("Total Red Flags Detected", len(analysis.get("red_flags", [])))

        # Audit Exploration Tabs
        tab_summary, tab_risks, tab_checklist, tab_chat = st.tabs([
            "📋 Plain Summary", 
            "🚩 Red Flag Radar", 
            "✅ Lawyer Checklist", 
            "💬 Ask Document (Q&A)"
        ])

        with tab_summary:
            st.subheader("Document Breakdown in Plain English")
            st.write(analysis.get("summary", "No summary available."))
            
            st.markdown("#### Key Obligations You Agree To:")
            for item in analysis.get("key_obligations", []):
                st.markdown(f"- {item}")

        with tab_risks:
            st.subheader("Critical Clauses & Risk Warnings")
            red_flags = analysis.get("red_flags", [])
            if not red_flags:
                st.info("No critical risks or one-sided penalties flagged!")
            else:
                for idx, flag in enumerate(red_flags, start=1):
                    severity = flag.get("severity", "Medium")
                    with st.expander(f"Clause {idx}: {flag.get('clause_name')} ({severity} Risk)", expanded=True):
                        st.markdown(f"**Potential Trap / Concern:** {flag.get('concern')}")
                        st.markdown(f"**Recommended Action / Revision:** :green[{flag.get('recommendation')}]")

        with tab_checklist:
            st.subheader("Questions to Ask a Professional Before Signing")
            st.markdown("Bring these exact points to your lawyer, counsel, or HR:")
            for item in analysis.get("lawyer_checklist", []):
                st.checkbox(item, key=f"check_{item}")

        with tab_chat:
            st.subheader("Chat Grounded in Your Document")
            st.caption("Ask specific questions like: 'What is the notice period?' or 'Are penalties unilateral?'")

            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            user_query = st.chat_input("Ask any specific question regarding clauses, termination, or penalties...")
            if user_query:
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)

                with st.chat_message("assistant"):
                    with st.spinner("Searching document clauses for grounded answers..."):
                        qa_prompt = (
                            "You are a helpful legal assistant. Answer the user question based SOLELY on the document text provided below.\n"
                            "Cite exact clause sections or quotes wherever possible. If the answer cannot be found in the document, state that clearly.\n\n"
                            f"DOCUMENT TEXT:\n{doc_text}\n\n"
                            f"QUESTION: {user_query}"
                        )
                        try:
                            response = generate_with_fallback(client, contents=[qa_prompt])
                            answer = response.text
                        except Exception as e:
                            answer = f"Error generating grounded answer: {e}"

                        st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})

                        