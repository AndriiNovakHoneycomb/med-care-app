from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime, timedelta
import os

def create_sample_documents():
    # Create directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'medical_documents')
    os.makedirs(output_dir, exist_ok=True)
    
    # Common styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20
    )
    
    # 1. Blood Test Report
    def create_blood_test():
        doc = SimpleDocTemplate(
            os.path.join(output_dir, "blood_test_report.pdf"),
            pagesize=letter
        )
        story = []
        
        # Title
        story.append(Paragraph("Complete Blood Count (CBC) Report", title_style))
        story.append(Paragraph(f"Test Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Test Results Table
        data = [
            ['Test', 'Result', 'Reference Range', 'Units'],
            ['WBC', '7.2', '4.0-11.0', '10^3/µL'],
            ['RBC', '4.8', '4.5-5.5', '10^6/µL'],
            ['Hemoglobin', '14.2', '13.5-17.5', 'g/dL'],
            ['Hematocrit', '42', '41-50', '%'],
            ['Platelets', '250', '150-450', '10^3/µL'],
            ['Neutrophils', '60', '40-70', '%'],
            ['Lymphocytes', '30', '20-40', '%'],
        ]
        
        table = Table(data, colWidths=[120, 100, 120, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        doc.build(story)
    
    # 2. Medical History Report
    def create_medical_history():
        doc = SimpleDocTemplate(
            os.path.join(output_dir, "medical_history.pdf"),
            pagesize=letter
        )
        story = []
        
        story.append(Paragraph("Medical History Report", title_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        sections = {
            "Past Medical Conditions": [
                "Hypertension - Diagnosed 2020",
                "Type 2 Diabetes - Diagnosed 2019",
                "Seasonal Allergies"
            ],
            "Surgical History": [
                "Appendectomy - 2015",
                "Knee Arthroscopy - 2018"
            ],
            "Current Medications": [
                "Lisinopril 10mg daily",
                "Metformin 500mg twice daily",
                "Cetirizine 10mg as needed"
            ],
            "Allergies": [
                "Penicillin - Severe rash",
                "Sulfa drugs - Mild rash",
                "Pollen - Seasonal symptoms"
            ],
            "Family History": [
                "Father: Hypertension, Coronary Artery Disease",
                "Mother: Type 2 Diabetes",
                "Sibling: No significant conditions"
            ]
        }
        
        for title, items in sections.items():
            story.append(Paragraph(title, header_style))
            for item in items:
                story.append(Paragraph(f"• {item}", styles['Normal']))
            story.append(Spacer(1, 20))
        
        doc.build(story)
    
    # 3. Radiology Report
    def create_radiology_report():
        doc = SimpleDocTemplate(
            os.path.join(output_dir, "chest_xray_report.pdf"),
            pagesize=letter
        )
        story = []
        
        story.append(Paragraph("Chest X-Ray Report", title_style))
        story.append(Paragraph(f"Examination Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        sections = {
            "Examination": "Chest X-Ray PA and Lateral Views",
            "Clinical History": "Annual check-up, no specific symptoms",
            "Technique": "Standard PA and lateral chest radiographs were obtained",
            "Findings": """
            Heart size and mediastinal contours are within normal limits.
            Lungs are clear without focal consolidation, effusion, or pneumothorax.
            No pleural abnormalities.
            Visualized bony structures show no acute abnormality.
            """,
            "Impression": "Normal chest X-ray. No acute cardiopulmonary process."
        }
        
        for title, content in sections.items():
            story.append(Paragraph(title, header_style))
            story.append(Paragraph(content, styles['Normal']))
            story.append(Spacer(1, 20))
        
        doc.build(story)
    
    # Generate all documents
    create_blood_test()
    create_medical_history()
    create_radiology_report()
    
    return [
        {
            'path': os.path.join(output_dir, "blood_test_report.pdf"),
            'title': 'Blood Test Results',
            'type': 'lab_report'
        },
        {
            'path': os.path.join(output_dir, "medical_history.pdf"),
            'title': 'Medical History Report',
            'type': 'medical_history'
        },
        {
            'path': os.path.join(output_dir, "chest_xray_report.pdf"),
            'title': 'Chest X-Ray Report',
            'type': 'radiology_report'
        }
    ]

if __name__ == '__main__':
    create_sample_documents() 