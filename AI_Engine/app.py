import streamlit as st
import ollama
from fpdf import FPDF
from datetime import datetime
import os

# PAGE CONFIG

st.set_page_config(
    page_title="Articles Daily+ AI",
    layout="wide"
)

st.title("📚 Articles Daily+ PDF Generator")

st.markdown("Convert raw articles into CAT VARC style PDFs automatically.")

# CREATE PDF FOLDER

os.makedirs("pdfs", exist_ok=True)

# ARTICLE INPUTS

article1 = st.text_area("Paste Article 1", height=250)
article2 = st.text_area("Paste Article 2", height=250)
article3 = st.text_area("Paste Article 3", height=250)
article4 = st.text_area("Paste Article 4", height=250)

articles = [article1, article2, article3, article4]

# BUTTON

if st.button("Generate PDF"):

    generated_content = []

    for i, article in enumerate(articles, start=1):

        if article.strip() == "":
            continue

        st.divider()

        st.header(f"Processing Article {i}")

        prompt = f"""
You are a CAT VARC expert.

Take the raw article and convert it into a professionally formatted CAT RC style article.

Then generate analysis in EXACTLY this structure:

Article - {i}

[Cleaned CAT style article]

Main idea of each paragraph

| Paragraph | Main Idea Sentence | Simpler Meaning |

Words to note
- Difficult word – Meaning

Tone

Conclusion

Word Count

Flesch Kincaid Difficulty Level

IMPORTANT:
- Clean formatting properly
- Improve readability
- Maintain original meaning
- Make article visually clean
- Keep professional coaching institute style

Raw Article:
{article}
"""

        with st.spinner(f"Generating Article {i}..."):

            response = ollama.chat(
                model='gemma3:1b',
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )

            result = response['message']['content']

            generated_content.append(result)

            st.markdown(result)

    # PDF GENERATION

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # COVER PAGE

    pdf.add_page()

    pdf.set_font("Arial", "B", 24)
    pdf.cell(200, 20, "Articles Daily+", ln=True, align='C')

    pdf.set_font("Arial", "", 16)

    today = datetime.now().strftime("%d %B %Y")

    pdf.cell(200, 10, today, ln=True, align='C')

    pdf.ln(30)

    pdf.set_font("Arial", "", 12)

    pdf.multi_cell(
        0,
        10,
        "Premium CAT VARC Reading Material"
    )

    # ARTICLE PAGES

    for content in generated_content:

        pdf.add_page()

        pdf.set_font("Arial", "", 11)

        cleaned_text = content.encode('latin-1', 'replace').decode('latin-1')

        pdf.multi_cell(0, 8, cleaned_text)

    # SAVE PDF

    pdf_path = f"pdfs/articles_daily_plus.pdf"

    pdf.output(pdf_path)

    st.success("PDF Generated Successfully!")

    # DOWNLOAD BUTTON

    with open(pdf_path, "rb") as file:

        st.download_button(
            label="📥 Download PDF",
            data=file,
            file_name="Articles_Daily_Plus.pdf",
            mime="application/pdf"
        )