import os
import streamlit as st
import openai
import PyPDF2
from fpdf import FPDF

# Configure OpenAI API Key
# Read from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

def extract_text_from_pdf(file):
    # Extracts text from the uploaded PDF file
    pdf_reader = PyPDF2.PdfReader(file)
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    return extracted_text

def generate_questions(text):
    # Call the OpenAI API to generate questions from the extracted text
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Give me some questions written in latex generated from this lecture notes. make sure the questions reflect and cover complete materials."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

def generate_latex_pdf(questions, output_path):
    # Generates a PDF in LaTeX format
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Generated Questions - Stellar Astrophysics", ln=True, align='C')

    pdf.ln(10)  # Line break
    pdf.set_font("Arial", size=12)

    # Write the questions in LaTeX format
    questions_list = questions.split("\n")
    for question in questions_list:
        pdf.multi_cell(0, 10, question)

    # Save the PDF
    pdf.output(output_path)

# Streamlit Web App
st.title("Lecture Notes to LaTeX PDF Question Generator")

# File upload
uploaded_file = st.file_uploader("Upload your lecture notes or paper (PDF format)", type=["pdf"])

if uploaded_file is not None:
    st.write("Processing the uploaded file...")
    
    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(uploaded_file)
    st.write("Text extracted successfully.")

    # Generate questions using OpenAI API
    if st.button("Generate Questions"):
        with st.spinner('Generating questions...'):
            questions = generate_questions(extracted_text)
            st.text_area("Generated Questions", value=questions, height=300)

            # Option to generate PDF in LaTeX format
            if st.button("Generate PDF"):
                output_path = "generated_questions.pdf"
                generate_latex_pdf(questions, output_path)
                st.success(f"PDF generated successfully! [Download it here](./{output_path})")

