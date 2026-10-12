# Script to assemble the complete AthleteShield Thesis Report docx
import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from generate_report import (
    DOC_DIR, FIG_DIR, add_p, add_bullet, add_chapter_title,
    add_h1, add_h2, add_h3, add_figure, add_equation,
    add_table_data, add_callout_algorithm, set_cell_background,
    set_cell_margins, set_table_borders
)

doc = docx.Document()

# Page Margins: Academic standard
for s in doc.sections:
    s.top_margin = Inches(1.0)
    s.bottom_margin = Inches(1.0)
    s.left_margin = Inches(1.25)
    s.right_margin = Inches(1.0)

print("Initialized document with academic margins.")
