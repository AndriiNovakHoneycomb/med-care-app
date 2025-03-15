from backend.app import celery, db
from backend.app.models import MedicalDocument
from backend.app.utils.storage import get_file_from_s3
import openai
from flask import current_app
import logging
from pypdf import PdfReader
import io

@celery.task
def generate_document_summary(document_id):
    """Generate a summary of a medical document using OpenAI's GPT model"""
    try:
        # Get document from database
        document = MedicalDocument.query.get(document_id)
        if not document:
            logging.error(f"Document {document_id} not found")
            return
        
        # Get file from S3
        file_obj = get_file_from_s3(document.file_path)
        
        # Extract text based on file type
        text = extract_text(file_obj, document.file_path)
        
        # Generate summary using OpenAI
        summary = generate_summary_with_openai(text)
        
        # Update document with summary
        document.summary = summary
        db.session.commit()
        
        return True
    except Exception as e:
        logging.error(f"Error generating summary for document {document_id}: {e}")
        return False

def extract_text(file_obj, file_path):
    """Extract text from various file types"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_obj)
    else:
        # For now, assume it's a text file
        return file_obj.read().decode('utf-8')

def extract_text_from_pdf(file_obj):
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_obj.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise

def generate_summary_with_openai(text):
    """Generate summary using OpenAI's GPT model"""
    try:
        openai.api_key = current_app.config['AI_API_KEY']
        
        # Truncate text if too long (adjust max_tokens based on your needs)
        max_chars = 3000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical document summarizer. Create a concise, professional summary of the following medical document."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating summary with OpenAI: {e}")
        raise 