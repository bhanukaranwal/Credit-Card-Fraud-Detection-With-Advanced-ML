from fpdf import FPDF
import os

def generate_report(shap_img_path, bias_report, output_pdf="compliance_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, "Fraud Detection Compliance Report", ln=True)
    
    if shap_img_path and os.path.exists(shap_img_path):
        pdf.image(shap_img_path, x=10, y=30, w=180)
    
    pdf.ln(85)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Fairness Audit Results:", ln=True)
    
    for attr, gap in bias_report:
        pdf.cell(200, 10, f"{attr} Gap: {gap:.2%}", ln=True)
    
    pdf.output(output_pdf)
    return output_pdf
