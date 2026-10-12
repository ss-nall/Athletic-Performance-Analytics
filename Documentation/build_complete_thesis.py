# build_complete_thesis.py
# Main driver script that builds the complete AthleteShield Thesis Report in DOCX & PDF
import os
import sys
import docx

import build_full_document
import chapters_writer
import chapters_writer_3_4_5
import chapter_4_writer

def main():
    print("Step 1: Generating Front Matter...")
    doc = build_full_document.build_report()

    print("Step 2: Generating Chapters 1 & 2...")
    doc = chapters_writer.write_all_chapters(doc)

    print("Step 3: Generating Chapter 3...")
    doc = chapters_writer_3_4_5.write_chapters_3_4_5(doc)

    print("Step 4: Generating Chapters 4, 5 and References...")
    doc = chapter_4_writer.write_chapter_4_5_refs(doc)

    out_docx = r"c:\Users\hp\OneDrive\Desktop\projects\Predictive\Documentation\AthleteShield_Report_Comprehensive.docx"
    doc.save(out_docx)
    print(f"Successfully saved comprehensive DOCX to: {out_docx}")

    # Step 5: Export to PDF using Word COM automation
    out_pdf = r"c:\Users\hp\OneDrive\Desktop\projects\Predictive\Documentation\AthleteShield_Report_Comprehensive.pdf"
    print("Step 5: Exporting to PDF via Microsoft Word COM automation...")
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc_word = word.Documents.Open(os.path.abspath(out_docx))
        
        # Update Table of Contents and fields if possible
        try:
            for toc in doc_word.TablesOfContents:
                toc.Update()
            for field in doc_word.Fields:
                field.Update()
        except Exception as e_toc:
            print(f"TOC update note: {e_toc}")
            
        doc_word.SaveAs(os.path.abspath(out_pdf), FileFormat=17) # 17 is wdFormatPDF
        doc_word.Close()
        word.Quit()
        print(f"Successfully generated PDF: {out_pdf}")
    except Exception as e_word:
        print(f"Word COM PDF export notice: {e_word}")

if __name__ == "__main__":
    main()
