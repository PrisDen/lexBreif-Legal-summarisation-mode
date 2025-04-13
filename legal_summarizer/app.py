from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import PyPDF2
import docx
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='static')

# Configure CORS to allow requests from any origin
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

# Initialize the summarization model
try:
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
except:
    # Fallback to a simpler model if the first one fails
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    except:
        print("Warning: Could not load preferred summarization models. Using text extraction only.")
        summarizer = None

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

for folder in [UPLOAD_FOLDER, REPORTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_dates(text):
    # Regular expressions for different date formats
    date_patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # DD/MM/YYYY or DD-MM-YYYY
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY/MM/DD or YYYY-MM-DD
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'  # Month DD, YYYY
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    
    return list(set(dates))  # Remove duplicates

def classify_importance(text):
    # Keywords for different importance levels
    high_importance = ['urgent', 'critical', 'immediate', 'deadline', 'must', 'required', 'mandatory']
    medium_importance = ['important', 'significant', 'consider', 'should', 'recommended']
    
    sentences = text.split('.')
    importance = {
        'high': [],
        'medium': [],
        'low': []
    }
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check for high importance keywords
        if any(keyword in sentence.lower() for keyword in high_importance):
            importance['high'].append(sentence)
        # Check for medium importance keywords
        elif any(keyword in sentence.lower() for keyword in medium_importance):
            importance['medium'].append(sentence)
        # Everything else is low importance
        else:
            importance['low'].append(sentence)
    
    # Limit the number of items in each category
    for key in importance:
        importance[key] = importance[key][:5]  # Keep only top 5 items
    
    return importance

def process_document(file_path):
    # Extract text based on file type
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension == 'docx':
        text = extract_text_from_docx(file_path)
    else:  # txt file
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    
    # Generate summary
    if summarizer:
        # Split text into chunks if it's too long
        max_chunk_length = 1024
        chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        
        summaries = []
        for chunk in chunks:
            if len(chunk.strip()) > 100:  # Only summarize chunks with substantial content
                try:
                    summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
                    summaries.append(summary[0]['summary_text'])
                except Exception as e:
                    print(f"Warning: Summarization failed for chunk: {str(e)}")
                    # Use the first few sentences as a fallback
                    sentences = chunk.split('.')[:3]
                    summaries.append('. '.join(sentences) + '.')
        
        final_summary = ' '.join(summaries)
    else:
        # If no summarizer is available, use the first few sentences as a summary
        sentences = text.split('.')[:5]  # First 5 sentences
        final_summary = '. '.join(sentences) + '.'
    
    # Extract dates
    dates = extract_dates(text)
    
    # Classify importance of content
    importance = classify_importance(text)
    
    return {
        'summary': final_summary,
        'dates': dates,
        'importance': importance
    }

def create_response(data=None, error=None, status=200):
    response = {
        'success': error is None,
        'data': data,
        'error': error
    }
    return jsonify(response), status

def generate_pdf_report(data, original_filename):
    # Create a unique filename for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"legal_summary_report_{timestamp}.pdf"
    report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        report_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )
    
    # Build the document content
    content = []
    
    # Title
    content.append(Paragraph("Legal Document Summary Report", title_style))
    content.append(Paragraph(f"Original Document: {original_filename}", styles['Italic']))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}", styles['Italic']))
    content.append(Spacer(1, 20))
    
    # Summary Section
    content.append(Paragraph("Document Summary", heading_style))
    content.append(Paragraph(data['summary'], body_style))
    content.append(Spacer(1, 20))
    
    # Important Dates Section
    content.append(Paragraph("Important Dates", heading_style))
    if data['dates']:
        dates_list = ListFlowable(
            [ListItem(Paragraph(date, body_style)) for date in data['dates']],
            bulletType='bullet',
            leftIndent=20
        )
        content.append(dates_list)
    else:
        content.append(Paragraph("No important dates found.", body_style))
    content.append(Spacer(1, 20))
    
    # Key Information Sections
    content.append(Paragraph("Key Information", heading_style))
    
    # High Priority
    content.append(Paragraph("Very Important", ParagraphStyle(
        'Priority',
        parent=body_style,
        textColor=colors.HexColor('#c0392b')
    )))
    if data['importance']['high']:
        high_list = ListFlowable(
            [ListItem(Paragraph(item, body_style)) for item in data['importance']['high']],
            bulletType='bullet',
            leftIndent=20
        )
        content.append(high_list)
    
    # Medium Priority
    content.append(Paragraph("Important", ParagraphStyle(
        'Priority',
        parent=body_style,
        textColor=colors.HexColor('#d35400')
    )))
    if data['importance']['medium']:
        medium_list = ListFlowable(
            [ListItem(Paragraph(item, body_style)) for item in data['importance']['medium']],
            bulletType='bullet',
            leftIndent=20
        )
        content.append(medium_list)
    
    # Low Priority
    content.append(Paragraph("Additional Information", ParagraphStyle(
        'Priority',
        parent=body_style,
        textColor=colors.HexColor('#7f8c8d')
    )))
    if data['importance']['low']:
        low_list = ListFlowable(
            [ListItem(Paragraph(item, body_style)) for item in data['importance']['low']],
            bulletType='bullet',
            leftIndent=20
        )
        content.append(low_list)
    
    # Build the PDF
    doc.build(content)
    return report_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory(app.config['REPORTS_FOLDER'], filename)

@app.route('/summarize', methods=['POST', 'OPTIONS'])
def summarize():
    if request.method == 'OPTIONS':
        return create_response()
        
    try:
        if 'document' not in request.files:
            return create_response(error='No file provided', status=400)
        
        file = request.files['document']
        if file.filename == '':
            return create_response(error='No file selected', status=400)
        
        if not allowed_file(file.filename):
            return create_response(error='File type not allowed. Please upload PDF, DOCX, or TXT files.', status=400)
        
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the document
            result_data = process_document(filepath)
            
            # Generate PDF report
            report_filename = generate_pdf_report(result_data, filename)
            
            # Add the report URL to the response
            result_data['report_url'] = f'/reports/{report_filename}'
            
            return create_response(data=result_data)
            
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
        
    except Exception as e:
        return create_response(error=str(e), status=500)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 