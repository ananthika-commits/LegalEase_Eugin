"""
Gemini Document Generator
Integrates the modern, official Google GenAI SDK (google-genai) to generate
comprehensive, structured, and customized legal documents.
"""

import os
import re
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    """Core generator class interfacing with the modern Google GenAI Client."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip()
        self.client = None
        self._configured = False

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self._configured = True
            except Exception as e:
                print(f"[Warning] Failed to initialize Google GenAI Client: {e}")
                self._configured = False
        else:
            self._configured = False

    def is_configured(self) -> bool:
        """Returns True if a valid Google GenAI client is configured."""
        return self._configured and (self.client is not None)

    def _build_prompt(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        """Constructs an expert legal prompt for Gemini."""
        return f"""You are a senior legal counsel and expert contract drafting attorney. 
Draft a professional, legally binding, comprehensive, and unambiguous legal document based strictly on the parameters below.

### DOCUMENT SPECIFICATIONS:
- Document Type: {document_type}
- Involved Parties & Roles: {parties}
- Specific Terms & Agreed Clauses (semicolon-separated): {terms}
- Effective Date: {dates}

### DRAFTING REQUIREMENTS & STRUCTURE:
1. TITLE: Formal, uppercase document title (e.g., # EMPLOYMENT AGREEMENT).
2. PREAMBLE: Identify all parties, entity types/individual names, addresses, and state the Effective Date ({dates}).
3. RECITALS (WHEREAS clauses): Background context and purpose of the agreement.
4. DEFINITIONS: Clear definitions for capitalized key terms used throughout the document.
5. OPERATIVE COVENANTS & CLAUSES:
   - Deeply integrate each of the user-provided terms: "{terms}". 
   - Expand each term into clear, professional, enforceable clauses with sub-clauses, performance standards, deadlines, and remedies.
   - Do NOT just copy the terms verbatim—draft them in formal legal phrasing.
6. STANDARD LEGAL BOILERPLATE CLAUSES:
   - Confidentiality & Non-Disclosure (if applicable)
   - Term, Renewal & Termination (notice periods, breach remedies)
   - Representations and Warranties
   - Indemnification & Limitation of Liability
   - Governing Law and Dispute Resolution (arbitration/court jurisdiction)
   - Severability, Entire Agreement, and Amendments
7. EXECUTION & SIGNATURE BLOCKS: Include formal signature lines for all named parties, including Name, Title, Company Name, Signature, and Date.

### FORMATTING GUIDELINES:
- Use clean Markdown formatting:
  - Document Title: `# <TITLE>`
  - Section Headings: `## <SECTION NUMBER AND TITLE>`
  - Subsections: `### <SUBSECTION>` or numbered lists `1.1`, `1.2`.
- Avoid Markdown code blocks (do not enclose the entire response in ```markdown ... ```).
- Maintain an authoritative, formal, and precise legal tone suitable for immediate legal review and execution.
"""

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str
    ) -> Dict[str, Any]:
        """
        Generates a customized legal document.
        If Gemini API key is configured and valid, calls the official Google GenAI SDK.
        Otherwise, falls back to the high-fidelity template generator to ensure 100% availability.
        """
        # Parse terms into clean list
        raw_terms = [t.strip() for t in re.split(r"[;\n]", terms) if t.strip()]

        if self.is_configured() and self.client:
            try:
                prompt = self._build_prompt(document_type, parties, terms, dates)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,  # Low temperature for formal legal consistency
                        top_p=0.95,
                    )
                )

                if response and hasattr(response, "text") and response.text:
                    clean_content = response.text.strip()
                    # Strip wrapping code fences if model accidentally added them
                    if clean_content.startswith("```markdown"):
                        clean_content = clean_content[11:]
                    if clean_content.startswith("```"):
                        clean_content = clean_content[3:]
                    if clean_content.endswith("```"):
                        clean_content = clean_content[:-3]
                    clean_content = clean_content.strip()

                    return {
                        "success": True,
                        "document_type": document_type,
                        "content": clean_content,
                        "terms_list": raw_terms,
                        "parties": parties,
                        "effective_date": dates,
                        "model_used": f"Google {self.model_name} (google-genai)",
                        "source": "gemini_api"
                    }
            except Exception as e:
                print(f"[Error] Gemini API generation failed: {e}. Falling back to internal engine.")
                return self._generate_fallback(document_type, parties, raw_terms, dates, error_note=str(e))

        # Fallback when no API key configured
        return self._generate_fallback(document_type, parties, raw_terms, dates)

    def _generate_fallback(
        self,
        document_type: str,
        parties: str,
        terms_list: list,
        dates: str,
        error_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates a structured, legally sound document using high-fidelity templates."""
        title = document_type.upper() if document_type else "LEGAL AGREEMENT"

        # Split parties
        party_items = [p.strip() for p in parties.split(",") if p.strip()]
        if len(party_items) >= 2:
            party_a = party_items[0]
            party_b = party_items[1]
        elif len(party_items) == 1:
            party_a = party_items[0]
            party_b = "Counterparty / Client"
        else:
            party_a = "First Party"
            party_b = "Second Party"

        terms_clauses = ""
        for i, term in enumerate(terms_list, 1):
            terms_clauses += f"### 3.{i} Operative Clause {i}\n"
            terms_clauses += f"The Parties expressly covenant and agree that: **{term}**.\n\n"
            terms_clauses += f"Failure by either party to comply strictly with this obligation shall constitute a material breach of this Agreement, entitling the non-breaching party to seek immediate remedies as provided under applicable law.\n\n"

        if not terms_clauses:
            terms_clauses = "### 3.1 Agreed Scope\nThe Parties agree to fulfill all responsibilities outlined in mutual written communications.\n\n"

        content = f"""# {title}

**EFFECTIVE DATE:** {dates}

This {document_type} (the "Agreement") is entered into and made effective as of **{dates}** (the "Effective Date"), by and between:

- **Party A:** {party_a}
- **Party B:** {party_b}

(Hereinafter collectively referred to as the "Parties" and individually as a "Party").

---

## 1. RECITALS & PURPOSE
WHEREAS, the Parties desire to establish a formal legal relationship governed by the terms, covenants, and mutual promises set forth herein; and
WHEREAS, both Parties acknowledge receipt of good and valuable consideration, the sufficiency of which is hereby acknowledged;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the Parties agree as follows:

---

## 2. DEFINITIONS
2.1 **"Applicable Law"** means all applicable statutes, regulations, ordinances, and court orders governing the jurisdiction of this Agreement.
2.2 **"Confidential Information"** means all proprietary technical, financial, commercial, or operational information disclosed directly or indirectly between the Parties.
2.3 **"Effective Date"** means {dates}.

---

## 3. SPECIFIC COVENANTS AND OPERATIVE TERMS
{terms_clauses}
---

## 4. TERM AND TERMINATION
4.1 **Term:** This Agreement shall commence on the Effective Date ({dates}) and shall continue in full force and effect until terminated in accordance with the provisions herein or upon full satisfaction of all mutual covenants.
4.2 **Termination for Convenience:** Unless otherwise restricted in Section 3, either Party may terminate this Agreement by providing thirty (30) days' written notice to the other Party.
4.3 **Termination for Cause:** Either Party may terminate this Agreement immediately upon written notice if the other Party commits a material breach and fails to cure such breach within fifteen (15) days of receipt of notice.

---

## 5. CONFIDENTIALITY AND NON-DISCLOSURE
Each Party agrees to protect the Confidential Information of the other Party with the same degree of care it uses for its own confidential materials (and no less than reasonable care). Confidential Information shall not be disclosed to any third party without prior written consent, except as required by lawful court order.

---

## 6. REPRESENTATIONS AND WARRANTIES
Each Party represents and warrants that:
(a) It has full legal authority and capacity to enter into and perform this Agreement;
(b) This Agreement constitutes a valid, legal, and binding obligation enforceable in accordance with its terms;
(c) Its performance hereunder does not conflict with any other contractual or statutory duty.

---

## 7. GOVERNING LAW AND DISPUTE RESOLUTION
This Agreement shall be interpreted and governed in accordance with the laws of the applicable jurisdiction, without regard to principles of conflicts of law. Any dispute, controversy, or claim arising under or relating to this Agreement shall first be submitted to good-faith mediation before initiating formal legal proceedings.

---

## 8. MISCELLANEOUS PROVISIONS
8.1 **Entire Agreement:** This Agreement constitutes the complete and exclusive understanding between the Parties regarding the subject matter hereof, superseding all prior oral or written agreements.
8.2 **Severability:** If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.
8.3 **Amendments:** No modification or amendment of this Agreement shall be valid unless executed in writing and signed by both Parties.
8.4 **Counterparts:** This Agreement may be executed in counterparts, including electronic signatures, each of which shall be deemed an original.

---

## 9. EXECUTION AND SIGNATURES

IN WITNESS WHEREOF, the Parties hereto have caused this {document_type} to be duly executed by their authorized representatives as of the Effective Date.

| FOR PARTY A | FOR PARTY B |
| :--- | :--- |
| **Entity / Name:** {party_a} | **Entity / Name:** {party_b} |
| **Authorized Signature:** ____________________ | **Authorized Signature:** ____________________ |
| **Signatory Name:** __________________________ | **Signatory Name:** __________________________ |
| **Title:** ___________________________________ | **Title:** ___________________________________ |
| **Date:** {dates} | **Date:** {dates} |
"""

        note = f" (Offline fallback engine: {error_note})" if error_note else " (LegalEase High-Fidelity Drafting Engine)"
        return {
            "success": True,
            "document_type": document_type,
            "content": content,
            "terms_list": terms_list,
            "parties": parties,
            "effective_date": dates,
            "model_used": f"LegalEase Core Engine{note}",
            "source": "fallback"
        }
