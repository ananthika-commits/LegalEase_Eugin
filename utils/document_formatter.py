"""
Document Formatter & Export Utilities
Handles text sanitization and multi-format document generation (.docx, .pdf, .txt, .html).
"""

import io
import os
import re
from typing import List, Union, Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from fpdf import FPDF


def sanitize_text(text: str) -> str:
    """
    Cleans smart quotes, dashes, symbols, and non-ASCII/non-Latin characters
    to prevent encoding errors in PDF generation while preserving document structure.
    """
    if not text:
        return ""

    replacements = {
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u2013": "-",  # En dash
        "\u2014": " - ", # Em dash
        "\u2026": "...", # Ellipsis
        "\u00a0": " ",  # Non-breaking space
        "\u2022": "*",  # Bullet
        "\u25cf": "*",  # Black circle
        "\u2212": "-",  # Minus
        "\u2010": "-",  # Hyphen
        "\u2011": "-",  # Non-breaking hyphen
        "\u2012": "-",  # Figure dash
        "\u201e": '"',  # Double low-9 quotation mark
        "\u2032": "'",  # Prime
        "\u2033": '"',  # Double prime
    }

    for orig, rep in replacements.items():
        text = text.replace(orig, rep)

    # Encode to latin-1 compatible or strip unsupported chars for fpdf compatibility
    clean_chars = []
    for char in text:
        code = ord(char)
        if code < 256:
            clean_chars.append(char)
        else:
            clean_chars.append("?")
    return "".join(clean_chars)


def _set_cell_background(cell, hex_color: str):
    """Sets background color of a Word table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def format_docx(
    text: str,
    doc_type: str,
    terms: Optional[Union[List[str], str]] = None,
    parties: str = "",
    effective_date: str = "",
    logo_path: Optional[str] = None
) -> io.BytesIO:
    """
    Converts raw/markdown legal document text into a styled Microsoft Word (.docx) document.
    Features:
      - Embedded company logo (centered)
      - Times New Roman font throughout (12pt body, bold headings)
      - Key Terms summary table auto-generated from user inputs
      - Metadata block (Parties, Effective Date)
      - Running legal disclaimer in footer
    """
    doc = Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

        # Configure Header & Footer
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer_p.add_run(
            "LegalEase AI-Generated Document - Strictly for Informational and Drafting Purposes"
        )
        footer_run.font.name = "Times New Roman"
        footer_run.font.size = Pt(8.5)
        footer_run.font.italic = True
        footer_run.font.color.rgb = RGBColor(128, 128, 128)

    # Base style: Times New Roman
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)

    # 1. Embed Logo if available
    if logo_path and os.path.exists(logo_path):
        try:
            logo_p = doc.add_paragraph()
            logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            logo_run = logo_p.add_run()
            logo_run.add_picture(logo_path, width=Inches(1.8))
        except Exception as e:
            print(f"[Warning] Could not insert logo into docx: {e}")

    # 2. Document Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run((doc_type or "LEGAL AGREEMENT").upper())
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 32, 67) # Navy blue
    title_p.paragraph_format.space_after = Pt(12)

    # 3. Metadata summary box (Table)
    if parties or effective_date:
        meta_table = doc.add_table(rows=2, cols=2)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        meta_table.autofit = False

        headers = [("Effective Date:", effective_date or "As specified"),
                   ("Parties Involved:", parties or "As identified herein")]
        
        for idx, (label, val) in enumerate(headers):
            row = meta_table.rows[idx]
            cell_lbl, cell_val = row.cells[0], row.cells[1]
            cell_lbl.width = Inches(2.0)
            cell_val.width = Inches(4.5)

            _set_cell_background(cell_lbl, "F0F4F8")
            _set_cell_background(cell_val, "FAFAFA")
            _set_cell_margins(cell_lbl, 80, 80, 120, 120)
            _set_cell_margins(cell_val, 80, 80, 120, 120)

            p_l = cell_lbl.paragraphs[0]
            r_l = p_l.add_run(label)
            r_l.font.name = "Times New Roman"
            r_l.font.bold = True
            r_l.font.size = Pt(10)

            p_v = cell_val.paragraphs[0]
            r_v = p_v.add_run(val)
            r_v.font.name = "Times New Roman"
            r_v.font.size = Pt(10)

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 4. Terms Summary Table (if terms provided)
    clean_terms = []
    if isinstance(terms, list):
        clean_terms = [t.strip() for t in terms if t.strip()]
    elif isinstance(terms, str) and terms.strip():
        clean_terms = [t.strip() for t in re.split(r"[;\n]", terms) if t.strip()]

    if clean_terms:
        sec_p = doc.add_paragraph()
        sec_run = sec_p.add_run("SCHEDULE A: SUMMARY OF SPECIFIC AGREED TERMS")
        sec_run.font.name = "Times New Roman"
        sec_run.font.size = Pt(12)
        sec_run.font.bold = True
        sec_run.font.color.rgb = RGBColor(15, 32, 67)
        sec_p.paragraph_format.space_after = Pt(4)

        terms_table = doc.add_table(rows=1 + len(clean_terms), cols=2)
        terms_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        terms_table.autofit = False

        # Header row
        hdr_cells = terms_table.rows[0].cells
        hdr_cells[0].width = Inches(0.8)
        hdr_cells[1].width = Inches(5.7)
        _set_cell_background(hdr_cells[0], "1B365D")
        _set_cell_background(hdr_cells[1], "1B365D")
        _set_cell_margins(hdr_cells[0], 100, 100, 120, 120)
        _set_cell_margins(hdr_cells[1], 100, 100, 120, 120)

        p0 = hdr_cells[0].paragraphs[0]
        r0 = p0.add_run("Item")
        r0.font.name = "Times New Roman"
        r0.font.bold = True
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(255, 255, 255)

        p1 = hdr_cells[1].paragraphs[0]
        r1 = p1.add_run("Operative Term / Condition")
        r1.font.name = "Times New Roman"
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(255, 255, 255)

        for i, t in enumerate(clean_terms, 1):
            row_cells = terms_table.rows[i].cells
            row_cells[0].width = Inches(0.8)
            row_cells[1].width = Inches(5.7)
            bg = "F7F9FB" if i % 2 == 1 else "FFFFFF"
            _set_cell_background(row_cells[0], bg)
            _set_cell_background(row_cells[1], bg)
            _set_cell_margins(row_cells[0], 80, 80, 120, 120)
            _set_cell_margins(row_cells[1], 80, 80, 120, 120)

            rp0 = row_cells[0].paragraphs[0]
            rr0 = rp0.add_run(f"Clause {i}")
            rr0.font.name = "Times New Roman"
            rr0.font.size = Pt(9.5)
            rr0.font.bold = True

            rp1 = row_cells[1].paragraphs[0]
            rr1 = rp1.add_run(t)
            rr1.font.name = "Times New Roman"
            rr1.font.size = Pt(9.5)

        doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 5. Parse and Render Markdown Document Body
    lines = text.split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("# "):
            # Top title already added, skip or render as secondary header if different
            heading_text = line[2:].strip()
            if heading_text.upper() != (doc_type or "").upper():
                hp = doc.add_paragraph()
                hr = hp.add_run(heading_text)
                hr.font.name = "Times New Roman"
                hr.font.size = Pt(15)
                hr.font.bold = True
                hr.font.color.rgb = RGBColor(15, 32, 67)
                hp.paragraph_format.space_before = Pt(12)
                hp.paragraph_format.space_after = Pt(4)
        elif line.startswith("## "):
            heading_text = line[3:].strip()
            hp = doc.add_paragraph()
            hr = hp.add_run(heading_text)
            hr.font.name = "Times New Roman"
            hr.font.size = Pt(13)
            hr.font.bold = True
            hr.font.color.rgb = RGBColor(27, 54, 93)
            hp.paragraph_format.space_before = Pt(10)
            hp.paragraph_format.space_after = Pt(3)
        elif line.startswith("### "):
            heading_text = line[4:].strip()
            hp = doc.add_paragraph()
            hr = hp.add_run(heading_text)
            hr.font.name = "Times New Roman"
            hr.font.size = Pt(11.5)
            hr.font.bold = True
            hr.font.color.rgb = RGBColor(40, 40, 40)
            hp.paragraph_format.space_before = Pt(6)
            hp.paragraph_format.space_after = Pt(2)
        elif line.startswith("---") or line.startswith("***"):
            # Divider
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run("____________________________________________________________________")
            r.font.name = "Times New Roman"
            r.font.color.rgb = RGBColor(200, 200, 200)
        elif line.startswith("|") and line.endswith("|"):
            # Markdown table line - ignore markdown divider rows like | :--- | :--- |
            if re.match(r"^\|[\s\-:]+(\|[\s\-:]+)+\|$", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            for idx, c in enumerate(cells):
                r = p.add_run(c + ("  |  " if idx < len(cells) - 1 else ""))
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
                if "**" in c:
                    r.font.bold = True
        elif line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(style='List Bullet')
            bullet_text = line[2:].strip()
            _add_formatted_text(p, bullet_text)
            p.paragraph_format.space_after = Pt(2)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(4)
            _add_formatted_text(p, line)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def _add_formatted_text(paragraph, text: str):
    """Parses simple inline markdown bold (**bold**) and regular text."""
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.font.name = "Times New Roman"
            run.font.bold = True
        else:
            run = paragraph.add_run(part)
            run.font.name = "Times New Roman"


class LegalPDF(FPDF):
    """Custom FPDF class with legal header, footer, and page numbering."""

    def __init__(self, doc_type: str = "Legal Agreement", logo_path: Optional[str] = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.doc_type = sanitize_text(doc_type)
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # Center logo on page
                self.image(self.logo_path, x=85, y=10, w=40)
                self.ln(18)
            except Exception:
                pass
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f"LegalEase | {self.doc_type.upper()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        # LegalEase Confidential Disclaimer and Page Numbers
        self.cell(140, 5, "LegalEase AI-Generated Document - For Legal Review & Drafting Purposes", align="L")
        self.cell(50, 5, f"Page {self.page_no()}/{{nb}}", align="R")


def format_pdf(
    text: str,
    doc_type: str,
    terms: Optional[Union[List[str], str]] = None,
    parties: str = "",
    effective_date: str = "",
    logo_path: Optional[str] = None
) -> io.BytesIO:
    """
    Renders legal document text into a styled PDF.
    Features:
      - Clean custom header with logo
      - Custom footer with page number and legal disclaimer
      - Bold headings with distinct typography
      - Safe ASCII / Latin-1 sanitization to avoid encoding faults
    """
    clean_text = sanitize_text(text)
    clean_doc_type = sanitize_text(doc_type)

    pdf = LegalPDF(doc_type=clean_doc_type, logo_path=logo_path)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Document Title
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(15, 32, 67) # Navy blue
    pdf.cell(0, 10, clean_doc_type.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Metadata (Date & Parties)
    if effective_date or parties:
        pdf.set_fill_color(240, 244, 248)
        pdf.rect(10, pdf.get_y(), 190, 18, style="F")
        pdf.set_xy(12, pdf.get_y() + 2)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(35, 5, "Effective Date: ", new_x="RIGHT")
        pdf.set_font("helvetica", "", 9)
        pdf.cell(0, 5, sanitize_text(effective_date or "As specified"), new_x="LMARGIN", new_y="NEXT")

        pdf.set_x(12)
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(35, 5, "Parties Involved: ", new_x="RIGHT")
        pdf.set_font("helvetica", "", 9)
        pdf.cell(0, 5, sanitize_text(parties or "As identified herein"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

    # Process Document Body lines
    lines = clean_text.split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            pdf.ln(2)
            continue

        if line.startswith("# "):
            title = line[2:].strip().upper()
            if title != clean_doc_type.upper():
                pdf.ln(3)
                pdf.set_font("helvetica", "B", 14)
                pdf.set_text_color(15, 32, 67)
                pdf.multi_cell(0, 7, title)
                pdf.ln(1)
        elif line.startswith("## "):
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(27, 54, 93)
            pdf.multi_cell(0, 6, line[3:].strip())
            pdf.ln(1)
        elif line.startswith("### "):
            pdf.ln(2)
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5, line[4:].strip())
        elif line.startswith("---") or line.startswith("***"):
            pdf.ln(2)
            pdf.set_draw_color(210, 210, 210)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
        elif line.startswith("|") and line.endswith("|"):
            # Table row or divider
            if re.match(r"^\|[\s\-:]+(\|[\s\-:]+)+\|$", line):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            pdf.set_font("helvetica", "", 8.5)
            pdf.set_text_color(40, 40, 40)
            col_width = 190 / max(len(cols), 1)
            for c in cols:
                pdf.cell(col_width, 5, sanitize_text(c.replace("**", "")), border=1)
            pdf.ln(5)
        elif line.startswith("- ") or line.startswith("* "):
            pdf.set_font("helvetica", "", 9.5)
            pdf.set_text_color(30, 30, 30)
            bullet_text = line[2:].strip().replace("**", "")
            pdf.set_x(14)
            pdf.cell(4, 5, chr(149), new_x="RIGHT") # Bullet point
            pdf.multi_cell(172, 5, bullet_text)
        else:
            pdf.set_font("helvetica", "", 9.5)
            pdf.set_text_color(30, 30, 30)
            plain_line = line.replace("**", "")
            pdf.multi_cell(0, 5, plain_line)

    buffer = io.BytesIO()
    pdf_bytes = pdf.output()
    buffer.write(pdf_bytes)
    buffer.seek(0)
    return buffer


def format_html_preview(text: str, doc_type: str = "") -> str:
    """
    Renders the legal document text into a stylized dark-themed scrollable HTML card
    with formal contract typography, accents, and dividers.
    """
    # Replace markdown headings and styles with HTML tags
    html_lines = []
    lines = text.split("\n")

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            html_lines.append("<div style='height: 10px;'></div>")
            continue

        # Bold formatting
        line_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)

        if line.startswith("# "):
            title = line_html[2:].strip()
            html_lines.append(f"<h1 style='color: #60a5fa; font-size: 1.5rem; text-align: center; margin-top: 15px; margin-bottom: 10px; font-family: Georgia, serif; text-transform: uppercase; letter-spacing: 1px;'>{title}</h1>")
        elif line.startswith("## "):
            sec_title = line_html[3:].strip()
            html_lines.append(f"<h2 style='color: #93c5fd; font-size: 1.15rem; margin-top: 18px; margin-bottom: 6px; font-family: Georgia, serif; border-bottom: 1px solid #334155; padding-bottom: 4px;'>{sec_title}</h2>")
        elif line.startswith("### "):
            sub_title = line_html[4:].strip()
            html_lines.append(f"<h3 style='color: #cbd5e1; font-size: 1.0rem; margin-top: 12px; margin-bottom: 4px; font-family: Georgia, serif;'>{sub_title}</h3>")
        elif line.startswith("---") or line.startswith("***"):
            html_lines.append("<hr style='border: none; border-top: 1px dashed #475569; margin: 15px 0;' />")
        elif line.startswith("- ") or line.startswith("* "):
            bullet_content = line_html[2:].strip()
            html_lines.append(f"<li style='margin-left: 20px; margin-bottom: 4px; color: #e2e8f0; line-height: 1.6;'>{bullet_content}</li>")
        elif line.startswith("|") and line.endswith("|"):
            if re.match(r"^\|[\s\-:]+(\|[\s\-:]+)+\|$", line):
                continue
            cols = [c.strip() for c in line_html.strip("|").split("|")]
            cols_html = "".join([f"<td style='padding: 6px 12px; border: 1px solid #334155; color: #cbd5e1;'>{c}</td>" for c in cols])
            html_lines.append(f"<table style='width: 100%; border-collapse: collapse; margin: 8px 0;'><tr>{cols_html}</tr></table>")
        else:
            html_lines.append(f"<p style='color: #e2e8f0; margin-bottom: 6px; line-height: 1.65; font-size: 0.95rem;'>{line_html}</p>")

    body_content = "\n".join(html_lines)

    html_container = f"""
    <div style="
        background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 28px;
        color: #f8fafc;
        font-family: 'Times New Roman', Georgia, serif;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 15px;">
            <span style="font-size: 0.85rem; font-weight: 600; color: #38bdf8; text-transform: uppercase; letter-spacing: 1.5px;">
                ⚖️ LegalEase Verified Draft
            </span>
            <span style="font-size: 0.75rem; background: #1e3a8a; color: #93c5fd; padding: 3px 8px; border-radius: 4px; border: 1px solid #2563eb;">
                AI-Generated Preview
            </span>
        </div>
        {body_content}
    </div>
    """
    return html_container
