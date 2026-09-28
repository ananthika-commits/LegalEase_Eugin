# LegalEase: AI-Powered Legal Document Generator

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini 1.5 Pro](https://img.shields.io/badge/Google-Gemini_1.5_Pro-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LegalEase** leverages Generative AI to simplify the creation of legal documents by providing customizable, structured, and editable agreements for a wide range of use cases. Users can generate **Employment Contracts**, **Residential Leases**, **Non-Disclosure Agreements (NDAs)**, **Freelance Work Agreements**, and more—all tailored to their specific inputs like involved parties, effective dates, and key terms.

---

## Architecture Overview

```
                               ┌────────────────────────────────┐
                               │       Streamlit Frontend       │
                               │      (http://localhost:8501)   │
                               └──────────────┬─────────────────┘
                                              │ POST /generate
                                              ▼
                               ┌────────────────────────────────┐
                               │        FastAPI Backend         │
                               │     (http://127.0.0.1:8000)    │
                               └──────────────┬─────────────────┘
                                              │ Prompt Engineering
                                              ▼
                    ┌───────────────────────────────────────────────────┐
                    │               AI Core Engine                      │
                    │  Google Gemini 1.5 Pro  /  Offline High-Fidelity  │
                    └─────────────────────────┬─────────────────────────┘
                                              │ Generated Legal Text
                                              ▼
             ┌─────────────────────────────────────────────────────────────────┐
             │                   Export & Formatting Engine                    │
             │   • .DOCX (Times New Roman, Embedded Logo, Terms Table, Footer) │
             │   • .PDF  (Branded Header/Footer, Page Numbers, Safe Encoding)  │
             │   • .TXT  (Clean ASCII / Unicode Sanitized Text)                │
             │   • HTML  (Dark-Themed Semantic Parchment Card Preview)         │
             └─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
d:\Legal ease Eugin\
├── .env                          # Local environment variables (GEMINI_API_KEY, etc.)
├── .env.example                  # Template configuration file
├── .gitignore                    # Git ignore file
├── requirements.txt              # Pinned Python package dependencies
├── README.md                     # Project documentation & guides
│
├── .vscode/
│   ├── settings.json             # Python interpreter, pytest & formatting settings
│   └── launch.json               # One-click VS Code debug configurations
│
├── assets/
│   └── logo.png                  # LegalEase high-res branding emblem & crest
│
├── scripts/
│   └── generate_logo.py          # Script to generate the branding logo asset
│
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py       # Gemini 1.5 Pro integration & prompt engineering
│
├── utils/
│   ├── __init__.py
│   └── document_formatter.py     # sanitize_text, format_docx, format_pdf, format_html_preview
│
├── backend/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application & CORS
│   └── routes.py                 # Pydantic schemas & API endpoints
│
├── main.py                       # Root FastAPI entry point
├── routes.py                     # Root API routes
├── app.py                        # Streamlit web application
│
├── tests/
│   ├── __init__.py
│   ├── test_backend.py           # Backend endpoints & validation tests
│   └── test_formatting.py        # PDF, DOCX, and text formatting tests
│
├── start_backend.bat             # Windows launcher for FastAPI
├── start_frontend.bat            # Windows launcher for Streamlit
└── run_all.bat                   # Concurrent launcher for complete stack
```

---

## Prerequisites

1. **Python 3.10+** (Developed and verified with Python 3.13.4).
2. **Google Gemini API Key** (Optional for live Gemini 1.5 Pro calls; get one at [Google AI Studio](https://aistudio.google.com/app/apikey)).
   *Note: If no API key is provided, LegalEase automatically runs with its built-in High-Fidelity Legal Drafting Engine.*

---

## Installation & Setup

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd "d:\Legal ease Eugin"
```

### Step 2: Create a Virtual Environment
```powershell
# Using Python 3.13:
& "C:\Users\anant\AppData\Local\Programs\Python\Python313\python.exe" -m venv .venv

# Or using the standard python command if added to PATH:
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
- **PowerShell**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Command Prompt**:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and set your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
FRONTEND_PORT=8501
```

---

## Running the Application

### Option A: One-Click Windows Launchers (Recommended)
Double-click:
- `run_all.bat` — Starts both FastAPI backend and Streamlit frontend concurrently.
- Or run `start_backend.bat` and `start_frontend.bat` individually.

### Option B: Terminal Commands
Open two terminal windows:

**Terminal 1 (Backend Server):**
```powershell
.\.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
- API Root: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Terminal 2 (Frontend App):**
```powershell
.\.venv\Scripts\python -m streamlit run app.py --server.port 8501
```
- Web Application: [http://localhost:8501](http://localhost:8501)

### Option C: VS Code One-Click Debugging
1. Open this folder in Visual Studio Code: `code .`
2. Select `.venv` as your Python Interpreter (`Ctrl+Shift+P` -> `Python: Select Interpreter`).
3. Press `F5` or go to the **Run & Debug** tab (`Ctrl+Shift+D`).
4. Select **"LegalEase: Full Stack (Backend + Frontend)"** and click the green Play button.

---

## Automated Testing

Run the comprehensive pytest suite verifying backend endpoints, Pydantic validation, and DOCX/PDF export engines:

```powershell
.\.venv\Scripts\pytest -v tests/
```

Expected output:
```
tests/test_backend.py::test_root_endpoint PASSED                         [ 11%]
tests/test_backend.py::test_health_endpoint PASSED                       [ 22%]
tests/test_backend.py::test_generate_document_success PASSED             [ 33%]
tests/test_backend.py::test_generate_document_missing_fields PASSED      [ 44%]
tests/test_backend.py::test_generate_document_empty_fields PASSED        [ 55%]
tests/test_formatting.py::test_sanitize_text PASSED                      [ 66%]
tests/test_formatting.py::test_format_docx_generation PASSED             [ 77%]
tests/test_formatting.py::test_format_pdf_generation PASSED              [ 88%]
tests/test_formatting.py::test_format_html_preview PASSED                [100%]
======================== 9 passed in 2.69s =========================
```

---

## Features & Usage Walkthrough

### 1. Document Input Parameters
- **Document Type**: Specify the contract type (e.g., *Employment Contract*, *NDA*, *Residential Lease Agreement*).
- **Involved Parties**: List all parties and roles (e.g., *Jane Doe (Service Provider), TechNova Inc. (Client)*).
- **Terms & Conditions**: Input key clauses separated by semicolons (`;`).
- **Effective Date**: Set the legal commencement date (e.g., *April 10, 2025*).

### 2. Preset Scenarios (Sidebar)
Easily load pre-configured scenarios with one click from the sidebar:
- 💼 *Freelance Work Contract*
- 🔒 *Non-Disclosure Agreement (NDA)*
- 🏠 *Residential Lease Agreement*
- 📄 *Employment Offer Letter*

### 3. Styled HTML Preview (Milestone 4.2)
View the AI-drafted document rendered inside an elegant, dark-themed scrollable card with clear typography, section dividers, and legal badges.

### 4. Inline Document Editor
Click **"✏️ Click to Edit Document"** to customize, fine-tune, or add custom clauses directly. Click **"💾 Save Changes"** to immediately update the document preview and all export formats.

### 5. Multi-Format Downloads
- 📄 **.TXT**: Clean ASCII/UTF-8 text file.
- 📝 **.DOCX**: Microsoft Word document formatted in Times New Roman (12pt body), with embedded logo, auto-generated **Terms Table**, and legal footer.
- 📑 **.PDF**: Branded PDF with custom header/logo, page numbers ("Page X of Y"), and legal disclaimer.

---

## API Reference

### `GET /`
Returns service status and welcome message.

### `GET /health`
Returns backend health status, API version, and AI model readiness.

### `POST /generate`
Generates a structured legal document.

**Request Payload:**
```json
{
  "document_type": "Freelance Work Contract",
  "parties": "Jane Doe (Provider), TechNova Inc. (Client)",
  "terms": "Payment within 30 days of invoice; Provider retains portfolio rights; Confidentiality maintained at all times",
  "dates": "April 10, 2025"
}
```

**Response Payload:**
```json
{
  "success": true,
  "document_type": "Freelance Work Contract",
  "content": "# FREELANCE WORK CONTRACT\n\n**EFFECTIVE DATE:** April 10, 2025...",
  "terms_list": [
    "Payment within 30 days of invoice",
    "Provider retains portfolio rights",
    "Confidentiality maintained at all times"
  ],
  "parties": "Jane Doe (Provider), TechNova Inc. (Client)",
  "effective_date": "April 10, 2025",
  "model_used": "Google gemini-1.5-pro",
  "source": "gemini_api",
  "generated_at": "2026-09-28 10:53:00"
}
```

---

## License
MIT License. Developed for automated legal document generation and drafting.
