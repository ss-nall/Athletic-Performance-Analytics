# build_full_document.py
# Full assembly of the comprehensive thesis report in exact example.pdf structure.

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from generate_report import (
    DOC_DIR, FIG_DIR, add_p, add_bullet, add_chapter_title,
    add_h1, add_h2, add_h3, add_figure, add_equation,
    add_table_data, add_callout_algorithm, set_cell_background,
    set_cell_margins, set_table_borders
)
import sections_data as sd

def build_report():
    doc = docx.Document()
    
    # Configure 1.25" Left, 1" Right, 1" Top/Bottom margins
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.25)
        s.right_margin = Inches(1.0)

    # ==========================================
    # 1. COVER PAGE / TITLE PAGE 1 (Matching example.pdf)
    # ==========================================
    add_p(doc, sd.TITLE, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=18, bold=True, size=15)
    add_p(doc, "PHASE II REPORT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=24, bold=True, size=13)
    add_p(doc, "Submitted by", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12, italic=True, size=12)
    
    for name, reg in sd.AUTHORS:
        add_p(doc, f"{name} ({reg})", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4, bold=True, size=12)
        
    add_p(doc, "\nin partial fulfillment for the award of the degree of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=12, italic=True, size=12)
    add_p(doc, sd.DEGREE, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=20, bold=True, size=13)
    
    # VIT Logo (image1.png)
    add_figure(doc, "image1.png", "", width=Inches(3.8))
    
    add_p(doc, sd.DEPARTMENT, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=4, bold=True, size=12)
    add_p(doc, sd.INSTITUTION, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4, bold=True, size=12)
    add_p(doc, sd.SUBMISSION_DATE, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12, bold=True, size=12)

    # ==========================================
    # 2. TITLE PAGE 2 (Thesis Title Page matching example.pdf)
    # ==========================================
    doc.add_page_break()
    add_p(doc, sd.TITLE, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=28, space_after=18, bold=True, size=15)
    add_p(doc, "A THESIS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=24, bold=True, size=13)
    add_p(doc, "Submitted by", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12, italic=True, size=12)
    
    for name, reg in sd.AUTHORS:
        add_p(doc, f"{name} ({reg})", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4, bold=True, size=12)
        
    add_p(doc, "\nin partial fulfillment for the award of the degree of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=12, italic=True, size=12)
    add_p(doc, sd.DEGREE, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=20, bold=True, size=13)
    
    add_figure(doc, "image1.png", "", width=Inches(3.8))
    
    add_p(doc, sd.DEPARTMENT, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=4, bold=True, size=12)
    add_p(doc, sd.INSTITUTION, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4, bold=True, size=12)
    add_p(doc, sd.SUBMISSION_DATE, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12, bold=True, size=12)

    # ==========================================
    # 3. BONAFIDE CERTIFICATE (Matching example.pdf page ii)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "VELLORE INSTITUTE OF TECHNOLOGY, VELLORE", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=14, bold=True, size=14)
    add_p(doc, "BONAFIDE CERTIFICATE", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=24, bold=True, size=14)
    
    cert_text = (
        f'Certified that this Project Report titled "{sd.TITLE}" is the bonafide work of '
        f'{sd.AUTHORS[0][0]} ({sd.AUTHORS[0][1]}) and {sd.AUTHORS[1][0]} ({sd.AUTHORS[1][1]}) '
        f'who carried out the project research under my direct supervision. Certified further that to the best of my knowledge '
        f'the work reported herein does not form part of any other thesis or dissertation on the basis of which a degree or award was '
        f'conferred on an earlier occasion on this or any other candidate.'
    )
    add_p(doc, cert_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=36, line_spacing=1.5)
    
    # Signature blocks table
    sig_tbl = doc.add_table(rows=2, cols=2)
    sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_tbl.columns[0].width = Inches(3.2)
    sig_tbl.columns[1].width = Inches(3.2)
    
    cell_s1 = sig_tbl.cell(0, 0)
    cell_s2 = sig_tbl.cell(0, 1)
    cell_t1 = sig_tbl.cell(1, 0)
    cell_t2 = sig_tbl.cell(1, 1)
    
    p = cell_s1.paragraphs[0]
    p.add_run("SIGNATURE\n\n\n\n").bold = True
    p = cell_s2.paragraphs[0]
    p.add_run("SIGNATURE\n\n\n\n").bold = True
    
    p = cell_t1.paragraphs[0]
    r = p.add_run(f"{sd.GUIDE}\n")
    r.bold = True
    p.add_run(f"PROJECT SUPERVISOR\n{sd.GUIDE_DESIGNATION}")
    
    p = cell_t2.paragraphs[0]
    r = p.add_run("HEAD OF THE DEPARTMENT\n")
    r.bold = True
    p.add_run(sd.HOD_DESIGNATION)

    # Remove borders from signature table
    tblPr = sig_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/><w:bottom w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # ==========================================
    # 4. ABSTRACT (ENGLISH) (Page iii)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "ABSTRACT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=18, bold=True, size=14)
    for p_txt in sd.ABSTRACT_EN:
        add_p(doc, p_txt, space_before=4, space_after=10, line_spacing=1.35)

    # ==========================================
    # 5. ABSTRACT (TAMIL) - சுருக்கம் (Page iv)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "சுருக்கம்", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=18, bold=True, size=14)
    for p_txt in sd.ABSTRACT_TA:
        add_p(doc, p_txt, space_before=4, space_after=10, line_spacing=1.35)

    # ==========================================
    # 6. ACKNOWLEDGEMENT (Page vi)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "ACKNOWLEDGEMENT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=18, bold=True, size=14)
    for p_txt in sd.ACKNOWLEDGEMENT:
        add_p(doc, p_txt, space_before=4, space_after=10, line_spacing=1.35)
        
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_auth.paragraph_format.space_before = Pt(20)
    for name, reg in sd.AUTHORS:
        r = p_auth.add_run(f"{name} ({reg})\n")
        r.bold = True

    # ==========================================
    # 7. TABLE OF CONTENTS (Pages vii - viii)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "TABLE OF CONTENTS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=14, bold=True, size=14)
    
    toc_tbl = doc.add_table(rows=len(sd.TOC_ITEMS)+1, cols=3)
    toc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_tbl.autofit = False
    toc_tbl.columns[0].width = Inches(1.1)
    toc_tbl.columns[1].width = Inches(4.5)
    toc_tbl.columns[2].width = Inches(0.9)
    
    # Headers
    h_c = toc_tbl.rows[0].cells
    h_c[0].text = "CHAPTER"
    h_c[1].text = "TITLE"
    h_c[2].text = "PAGE NO"
    for idx, c in enumerate(h_c):
        set_cell_background(c, "FFFFFF")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
        r = p.runs[0]
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        
    for r_idx, (num, title, pg) in enumerate(sd.TOC_ITEMS):
        row_cells = toc_tbl.rows[r_idx+1].cells
        row_cells[0].text = num
        row_cells[1].text = title
        row_cells[2].text = pg
        
        is_major = (num.endswith(".") or num == "") and not num.startswith("2.2") and not num.startswith("3.2") and not num.startswith("4.")
        
        for idx, c in enumerate(row_cells):
            set_cell_background(c, "FFFFFF")
            set_cell_margins(c, top=40, bottom=40, left=40, right=40)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
            if p.runs:
                r = p.runs[0]
                r.font.name = "Times New Roman"
                r.font.size = Pt(10.5 if is_major else 10)
                if is_major:
                    r.bold = True

    # Clean borders for TOC
    tblPr = toc_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # ==========================================
    # 8. LIST OF FIGURES (Page ix)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "LIST OF FIGURES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=14, bold=True, size=14)
    
    fig_tbl = doc.add_table(rows=len(sd.LIST_OF_FIGURES)+1, cols=3)
    fig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    fig_tbl.autofit = False
    fig_tbl.columns[0].width = Inches(1.1)
    fig_tbl.columns[1].width = Inches(4.5)
    fig_tbl.columns[2].width = Inches(0.9)
    
    h_c = fig_tbl.rows[0].cells
    h_c[0].text = "FIG. NO:"
    h_c[1].text = "DESCRIPTION"
    h_c[2].text = "PAGE NO"
    for idx, c in enumerate(h_c):
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
        r = p.runs[0]
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        
    for r_idx, (fnum, desc, pg) in enumerate(sd.LIST_OF_FIGURES):
        row_cells = fig_tbl.rows[r_idx+1].cells
        row_cells[0].text = fnum
        row_cells[1].text = desc
        row_cells[2].text = pg
        for idx, c in enumerate(row_cells):
            set_cell_margins(c, top=40, bottom=40, left=40, right=40)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
            if p.runs:
                r = p.runs[0]
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)

    tblPr = fig_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # ==========================================
    # 9. LIST OF TABLES (Page x)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "LIST OF TABLES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=14, bold=True, size=14)
    
    tab_tbl = doc.add_table(rows=len(sd.LIST_OF_TABLES)+1, cols=3)
    tab_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab_tbl.autofit = False
    tab_tbl.columns[0].width = Inches(1.1)
    tab_tbl.columns[1].width = Inches(4.5)
    tab_tbl.columns[2].width = Inches(0.9)
    
    h_c = tab_tbl.rows[0].cells
    h_c[0].text = "TABLE NO:"
    h_c[1].text = "DESCRIPTION"
    h_c[2].text = "PAGE NO"
    for idx, c in enumerate(h_c):
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
        r = p.runs[0]
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        
    for r_idx, (tnum, desc, pg) in enumerate(sd.LIST_OF_TABLES):
        row_cells = tab_tbl.rows[r_idx+1].cells
        row_cells[0].text = tnum
        row_cells[1].text = desc
        row_cells[2].text = pg
        for idx, c in enumerate(row_cells):
            set_cell_margins(c, top=40, bottom=40, left=40, right=40)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
            if p.runs:
                r = p.runs[0]
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)

    tblPr = tab_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # ==========================================
    # 10. LIST OF ABBREVIATIONS (Page xi)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "LIST OF ABBREVIATIONS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=14, bold=True, size=14)
    
    abb_tbl = doc.add_table(rows=len(sd.LIST_OF_ABBREVIATIONS)+1, cols=2)
    abb_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    abb_tbl.autofit = False
    abb_tbl.columns[0].width = Inches(2.0)
    abb_tbl.columns[1].width = Inches(4.5)
    
    h_c = abb_tbl.rows[0].cells
    h_c[0].text = "ABBREVIATION"
    h_c[1].text = "DESCRIPTION"
    for idx, c in enumerate(h_c):
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.runs[0]
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        
    for r_idx, (abb, desc) in enumerate(sd.LIST_OF_ABBREVIATIONS):
        row_cells = abb_tbl.rows[r_idx+1].cells
        row_cells[0].text = abb
        row_cells[1].text = desc
        for idx, c in enumerate(row_cells):
            set_cell_margins(c, top=35, bottom=35, left=40, right=40)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if p.runs:
                r = p.runs[0]
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)
                if idx == 0:
                    r.bold = True

    tblPr = abb_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # ==========================================
    # 11. LIST OF EQUATIONS (Page xii)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "LIST OF EQUATIONS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=14, bold=True, size=14)
    
    eq_tbl = doc.add_table(rows=len(sd.LIST_OF_EQUATIONS)+1, cols=3)
    eq_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    eq_tbl.autofit = False
    eq_tbl.columns[0].width = Inches(1.3)
    eq_tbl.columns[1].width = Inches(4.3)
    eq_tbl.columns[2].width = Inches(0.9)
    
    h_c = eq_tbl.rows[0].cells
    h_c[0].text = "EQUATION NO:"
    h_c[1].text = "TITLE"
    h_c[2].text = "PAGE NO"
    for idx, c in enumerate(h_c):
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
        r = p.runs[0]
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        
    for r_idx, (enum, title, pg) in enumerate(sd.LIST_OF_EQUATIONS):
        row_cells = eq_tbl.rows[r_idx+1].cells
        row_cells[0].text = enum
        row_cells[1].text = title
        row_cells[2].text = pg
        for idx, c in enumerate(row_cells):
            set_cell_margins(c, top=35, bottom=35, left=40, right=40)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx < 2 else WD_ALIGN_PARAGRAPH.RIGHT
            if p.runs:
                r = p.runs[0]
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)

    tblPr = eq_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    print("Front matter generated successfully.")
    return doc

print("Builder initialized.")
