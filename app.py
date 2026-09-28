"""
LegalEase: AI-Powered Legal Document Generator
Streamlit Frontend Web Application
"""

import os
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Import formatting engine
from utils.document_formatter import (
    sanitize_text,
    format_docx,
    format_pdf,
    format_html_preview,
)
from ai_core.gemini_generator import GeminiDocumentGenerator

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="LegalEase | AI-Powered Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    /* Global styling */
    .main-title {
        text-align: center;
        font-family: 'Georgia', serif;
        font-weight: 700;
        font-size: 2.2rem;
        color: #1e3a8a;
        margin-top: -10px;
        margin-bottom: 4px;
    }
    .sub-title {
        text-align: center;
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 25px;
    }
    .badge-status {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-online {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
    }
    .badge-offline {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fca5a5;
    }
    .stDownloadButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stDownloadButton button:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

# Preset templates for instant testing
PRESET_TEMPLATES = {
    "Freelance Work Contract": {
        "document_type": "Freelance Work Contract",
        "parties": "Jane Doe (Service Provider / Designer), TechNova Inc. (Client)",
        "terms": "Payment of $4,500 upon milestone completion within 30 days of invoice; Provider agrees to deliver final UI designs by May 15, 2025; Full intellectual property rights transfer upon final payment receipt; Confidentiality must be maintained at all times; Either party may terminate with 15 days written notice",
        "dates": "April 10, 2025"
    },
    "Non-Disclosure Agreement (NDA)": {
        "document_type": "Non-Disclosure Agreement (NDA)",
        "parties": "Alpha Innovations LLC (Disclosing Party), Beta Ventures Inc. (Receiving Party)",
        "terms": "Definition of Confidential Information includes source code, proprietary algorithms, financial models, and customer data; Receiving party agrees not to disclose information to any third party for a period of 3 years; Permitted use is solely for evaluating a joint business venture; Injunction relief available upon breach without posting bond; Return or certified destruction of materials within 10 days of request",
        "dates": "May 1, 2025"
    },
    "Residential Lease Agreement": {
        "document_type": "Residential Lease Agreement",
        "parties": "Arthur Pendelton (Landlord), Sarah Jenkins (Tenant)",
        "terms": "Monthly rent of $2,200 due on or before the 1st of each calendar month; Security deposit of $2,200 refundable within 21 days of lease expiration; Initial lease term of 12 consecutive months; Tenant responsible for electric and internet utilities; No unauthorized alterations or subletting without written consent; 30 days written notice required prior to lease renewal",
        "dates": "June 1, 2025"
    },
    "Employment Offer Letter": {
        "document_type": "Employment Offer Letter & Contract",
        "parties": "Apex Technologies Corp (Employer), Marcus Vance (Employee)",
        "terms": "Position of Senior Generative AI Engineer reporting to Chief Technology Officer; Starting base salary of $165,000 per annum plus standard employee healthcare and 401(k) match; At-will employment status governed by state law; Standard non-solicitation agreement active for 12 months following departure; 20 business days of paid annual leave",
        "dates": "July 1, 2025"
    }
}

# Initialize session state variables
if "doc_content" not in st.session_state:
    st.session_state.doc_content = ""
if "doc_type" not in st.session_state:
    st.session_state.doc_type = ""
if "parties_val" not in st.session_state:
    st.session_state.parties_val = ""
if "terms_val" not in st.session_state:
    st.session_state.terms_val = ""
if "dates_val" not in st.session_state:
    st.session_state.dates_val = ""
if "meta_info" not in st.session_state:
    st.session_state.meta_info = {}
if "is_editing" not in st.session_state:
    st.session_state.is_editing = False


# Helper: Check backend health
def check_backend_status():
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
        if res.status_code == 200:
            return True, res.json()
    except Exception:
        pass
    return False, {}


# --- SIDEBAR ---
with st.sidebar:
    st.title("⚖️ LegalEase Setup")
    
    # Live backend health monitor
    backend_online, backend_data = check_backend_status()
    if backend_online:
        st.markdown(
            '<div class="badge-status badge-online">● Backend Connected (Port 8000)</div>',
            unsafe_allow_html=True
        )
        gemini_ready = backend_data.get("gemini_configured", False)
        model_name = backend_data.get("model_target", "gemini-1.5-pro")
        if gemini_ready:
            st.caption(f"🤖 **Model:** `{model_name}` (Live API)")
        else:
            st.caption("ℹ️ *Running with High-Fidelity Local Drafting Engine (No API key set in .env)*")
    else:
        st.markdown(
            '<div class="badge-status badge-offline">● Backend Offline (Using Direct Engine)</div>',
            unsafe_allow_html=True
        )
        st.caption("Backend not detected on port 8000. Operating in standalone direct mode.")

    st.markdown("---")
    st.subheader("⚡ Quick Load Template")
    selected_preset = st.selectbox(
        "Choose a pre-configured scenario:",
        ["Select a template...", *PRESET_TEMPLATES.keys()]
    )

    if selected_preset != "Select a template...":
        preset = PRESET_TEMPLATES[selected_preset]
        if st.button("Apply Template Data", use_container_width=True, type="secondary"):
            st.session_state.doc_type = preset["document_type"]
            st.session_state.parties_val = preset["parties"]
            st.session_state.terms_val = preset["terms"]
            st.session_state.dates_val = preset["dates"]
            st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About LegalEase")
    st.markdown("""
    **LegalEase** empowers entrepreneurs and legal teams by auto-drafting comprehensive agreements.
    
    **Features:**
    - 🛡️ Structured legal clauses & recitals
    - 🖋️ Times New Roman formatted Word (.docx)
    - 📑 Header/footer branded PDF
    - ✏️ Inline editable document viewer
    """)


# --- HEADER & LOGO ---
col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_mid:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH)
    else:
        st.markdown("<h1 style='text-align: center;'>⚖️ LegalEase</h1>", unsafe_allow_html=True)

st.markdown('<div class="main-title">AI-Powered Legal Document Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Personalized, legally structured contracts and agreements in seconds</div>', unsafe_allow_html=True)

# --- USER INPUT FORM ---
st.subheader("1. Contract Parameters & Specifications")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        doc_type_input = st.text_input(
            "Document Type",
            value=st.session_state.doc_type,
            placeholder="e.g., Employment Contract, Non-Disclosure Agreement (NDA), Lease Agreement",
            help="Specify the kind of legal agreement or contract to draft."
        )
    with col2:
        dates_input = st.text_input(
            "Effective Date",
            value=st.session_state.dates_val,
            placeholder="e.g., April 10, 2025 or Effective immediately upon signing",
            help="The legal effective commencement date of the document."
        )

    parties_input = st.text_area(
        "Parties Involved (Names, Roles & Entities)",
        value=st.session_state.parties_val,
        height=70,
        placeholder="e.g., Jane Doe (Service Provider / Independent Contractor), TechNova Solutions Inc. (Client)",
        help="Identify all entities or individuals and their legal roles."
    )

    terms_input = st.text_area(
        "Terms & Conditions (Separate distinct clauses with semicolons ';')",
        value=st.session_state.terms_val,
        height=110,
        placeholder="e.g., Payment within 30 days of invoice; The provider agrees to deliver work by agreed deadline; Confidentiality must be maintained at all times; Either party may terminate with 15 days notice",
        help="Use semicolons (;) to separate each individual condition, rule, or covenant."
    )

    # Update session state with inputs
    st.session_state.doc_type = doc_type_input
    st.session_state.parties_val = parties_input
    st.session_state.terms_val = terms_input
    st.session_state.dates_val = dates_input

    # Generation Button
    generate_btn = st.button("🚀 Generate Document", type="primary", use_container_width=True)


# --- GENERATION LOGIC ---
if generate_btn:
    if not doc_type_input.strip() or not parties_input.strip() or not terms_input.strip() or not dates_input.strip():
        st.error("⚠️ Please fill in all fields before generating the document (Document Type, Parties, Terms, and Effective Date).")
    else:
        with st.spinner("🤖 Drafting professional legal document with AI..."):
            backend_success = False
            payload = {
                "document_type": doc_type_input.strip(),
                "parties": parties_input.strip(),
                "terms": terms_input.strip(),
                "dates": dates_input.strip()
            }

            # Attempt 1: Call FastAPI Backend
            try:
                resp = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.doc_content = data["content"]
                    st.session_state.meta_info = data
                    backend_success = True
            except Exception as e:
                # Backend unreachable, fall through to direct generator
                pass

            # Attempt 2: If Backend wasn't reached, use embedded Gemini/Fallback Generator
            if not backend_success:
                fallback_gen = GeminiDocumentGenerator()
                data = fallback_gen.generate_document(
                    document_type=payload["document_type"],
                    parties=payload["parties"],
                    terms=payload["terms"],
                    dates=payload["dates"]
                )
                st.session_state.doc_content = data["content"]
                st.session_state.meta_info = data

            st.success("✅ Legal document successfully generated!")
            st.rerun()


# --- PREVIEW, EDITING & DOWNLOADS ---
if st.session_state.doc_content:
    st.markdown("---")
    
    # Document Metrics Header
    words = len(st.session_state.doc_content.split())
    clauses = len([t for t in st.session_state.terms_val.split(";") if t.strip()])
    model_tag = st.session_state.meta_info.get("model_used", "LegalEase AI")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Document Type", st.session_state.doc_type[:20])
    m_col2.metric("Word Count", f"{words} words")
    m_col3.metric("Key Clauses", f"{clauses} terms")
    m_col4.metric("Engine", model_tag.split()[0] if model_tag else "AI")

    # Document Header Section
    st.subheader("2. Document Review & Customization")

    # Toggle Edit Mode button
    edit_col, view_col = st.columns([1, 4])
    with edit_col:
        if st.button("✏️ Click to Edit Document" if not st.session_state.is_editing else "👁️ Back to Styled Preview", use_container_width=True):
            st.session_state.is_editing = not st.session_state.is_editing
            st.rerun()

    # If in edit mode, display editable textarea
    if st.session_state.is_editing:
        st.info("💡 You are in **Edit Mode**. You can modify any clauses, names, or wording directly below.")
        edited_text = st.text_area(
            "Modify Document Text",
            value=st.session_state.doc_content,
            height=500,
            help="Make any changes to the legal clauses here."
        )
        if st.button("💾 Save Changes", type="primary"):
            st.session_state.doc_content = edited_text
            st.session_state.is_editing = False
            st.success("Changes saved!")
            st.rerun()
    else:
        # Display Dynamic Dark Card HTML Preview (Milestone 4.2)
        html_preview = format_html_preview(st.session_state.doc_content, st.session_state.doc_type)
        st.markdown(html_preview, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("3. Multi-Format Document Export")
    st.markdown("Download your customized legal document ready for printing, electronic signature, or legal review:")

    # Clean text for export
    clean_text = sanitize_text(st.session_state.doc_content)
    file_slug = (st.session_state.doc_type or "Document").replace(" ", "_").lower()

    # Generate Export Buffers
    # 1. Plain Text
    txt_data = clean_text.encode("utf-8")

    # 2. Word .docx
    try:
        docx_buffer = format_docx(
            text=st.session_state.doc_content,
            doc_type=st.session_state.doc_type,
            terms=st.session_state.terms_val,
            parties=st.session_state.parties_val,
            effective_date=st.session_state.dates_val,
            logo_path=LOGO_PATH if os.path.exists(LOGO_PATH) else None
        )
        docx_bytes = docx_buffer.getvalue()
    except Exception as e:
        docx_bytes = None
        st.error(f"Error preparing DOCX export: {e}")

    # 3. PDF
    try:
        pdf_buffer = format_pdf(
            text=st.session_state.doc_content,
            doc_type=st.session_state.doc_type,
            terms=st.session_state.terms_val,
            parties=st.session_state.parties_val,
            effective_date=st.session_state.dates_val,
            logo_path=LOGO_PATH if os.path.exists(LOGO_PATH) else None
        )
        pdf_bytes = pdf_buffer.getvalue()
    except Exception as e:
        pdf_bytes = None
        st.error(f"Error preparing PDF export: {e}")

    # Render Download Buttons in 3 columns
    d_col1, d_col2, d_col3 = st.columns(3)

    with d_col1:
        st.download_button(
            label="📄 Download as .TXT",
            data=txt_data,
            file_name=f"{file_slug}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with d_col2:
        if docx_bytes:
            st.download_button(
                label="📝 Download as .DOCX",
                data=docx_bytes,
                file_name=f"{file_slug}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    with d_col3:
        if pdf_bytes:
            st.download_button(
                label="📑 Download as .PDF",
                data=pdf_bytes,
                file_name=f"{file_slug}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
