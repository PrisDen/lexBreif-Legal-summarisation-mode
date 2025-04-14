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
from collections import defaultdict

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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

INDIAN_LAW_ARTICLES = {
    'Article 17': {
        'title': 'Abolition of Untouchability',
        'description': 'Article 17 of the Indian Constitution abolishes untouchability in all its forms and its practice is forbidden. Enforcing any disability arising from untouchability is a punishable offense.',
        'keywords': ['untouchability', 'caste discrimination', 'social discrimination', 'dalit', 'scheduled caste']
    },
    'Article 21': {
        'title': 'Protection of Life and Personal Liberty',
        'description': 'No person shall be deprived of his life or personal liberty except according to procedure established by law.',
        'keywords': ['life', 'liberty', 'personal freedom', 'fundamental rights', 'human rights']
    },
    'Article 14': {
        'title': 'Equality Before Law',
        'description': 'The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.',
        'keywords': ['equality', 'equal protection', 'discrimination', 'equal rights']
    },
    'Article 19': {
        'title': 'Protection of Certain Rights Regarding Freedom of Speech',
        'description': 'All citizens shall have the right to freedom of speech and expression, to assemble peaceably and without arms, to form associations or unions, to move freely throughout the territory of India, to reside and settle in any part of the territory of India, and to practice any profession, or to carry on any occupation, trade or business.',
        'keywords': ['freedom of speech', 'expression', 'assembly', 'association', 'movement', 'residence', 'profession']
    }
}

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
    
    dates_with_context = []
    for pattern in date_patterns:
        for match in re.finditer(pattern, text):
            date = match.group()
            # Get context (2 sentences before and after the date)
            start = max(0, text.rfind('.', 0, match.start()) + 1)
            end = text.find('.', match.end())
            if end == -1:
                end = len(text)
            context = text[start:end].strip()
            dates_with_context.append({
                'date': date,
                'context': context
            })
    
    # Remove duplicates based on date
    unique_dates = {}
    for item in dates_with_context:
        if item['date'] not in unique_dates:
            unique_dates[item['date']] = item['context']
    
    return [{'date': date, 'context': context} for date, context in unique_dates.items()]

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

def suggest_law_articles(text):
    try:
        # Load law articles from JSON file
        with open('data/indian_law_articles.json', 'r') as f:
            law_articles = json.load(f)['articles']
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Score each article based on keyword matches
        scored_articles = []
        for article in law_articles:
            score = 0
            for keyword in article['keywords']:
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > 0:
                scored_articles.append({
                    'article': article['article'],
                    'title': article['title'],
                    'description': article['description'],
                    'score': score
                })
        
        # Sort articles by score and return top 3
        scored_articles.sort(key=lambda x: x['score'], reverse=True)
        return [article for article in scored_articles[:3]]
    except Exception as e:
        print(f"Error suggesting law articles: {str(e)}")
        return []

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
    
    # Extract dates with context
    dates = extract_dates(text)
    
    # Suggest relevant law articles
    suggested_articles = suggest_law_articles(text)
    
    # Classify importance of content
    importance = classify_importance(text)
    
    return {
        'summary': final_summary,
        'dates': dates,
        'importance': importance,
        'suggested_articles': suggested_articles
    }

def create_response(data=None, error=None, status=200):
    response = {
        'success': error is None,
        'data': data,
        'error': error
    }
    return jsonify(response), status

def generate_pdf_report(data, original_filename):
    try:
        # Create a unique filename for the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"legal_summary_report_{timestamp}.pdf"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        # Create the PDF document with better margins
        doc = SimpleDocTemplate(
            report_path,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Custom styles
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=1
        )
        
        # Section header style
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.HexColor('#34495e'),
            fontName='Helvetica-Bold',
            leftIndent=10
        )
        
        # Content style
        content_style = ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50'),
            leading=14
        )
        
        # Date style
        date_style = ParagraphStyle(
            'CustomDate',
            parent=content_style,
            fontSize=12,
            textColor=colors.HexColor('#3498db'),
            fontName='Helvetica-Bold'
        )
        
        # Context style
        context_style = ParagraphStyle(
            'CustomContext',
            parent=content_style,
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            leftIndent=20
        )
        
        # Build the document content
        content = []
        
        # Title and metadata
        content.append(Paragraph("Legal Document Summary Report", title_style))
        content.append(Paragraph(f"Original Document: {original_filename}", subtitle_style))
        content.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}", subtitle_style))
        content.append(Spacer(1, 30))
        
        # Summary Section
        content.append(Paragraph("Document Summary", section_style))
        content.append(Paragraph(data.get('summary', 'No summary available'), content_style))
        content.append(Spacer(1, 20))
        
        # Important Dates Section
        content.append(Paragraph("Important Dates", section_style))
        if data.get('dates'):
            for date in data['dates']:
                content.append(Paragraph(date.get('date', ''), date_style))
                content.append(Paragraph(date.get('context', ''), context_style))
                content.append(Spacer(1, 10))
        else:
            content.append(Paragraph("No important dates found.", content_style))
        content.append(Spacer(1, 20))
        
        # Key Information Sections
        content.append(Paragraph("Key Information", section_style))
        
        # High Priority
        content.append(Paragraph("Critical Information", ParagraphStyle(
            'Priority',
            parent=content_style,
            textColor=colors.HexColor('#c0392b'),
            fontName='Helvetica-Bold'
        )))
        if data.get('importance', {}).get('high'):
            for item in data['importance']['high']:
                content.append(Paragraph(f"• {item}", content_style))
        content.append(Spacer(1, 10))
        
        # Medium Priority
        content.append(Paragraph("Important Information", ParagraphStyle(
            'Priority',
            parent=content_style,
            textColor=colors.HexColor('#d35400'),
            fontName='Helvetica-Bold'
        )))
        if data.get('importance', {}).get('medium'):
            for item in data['importance']['medium']:
                content.append(Paragraph(f"• {item}", content_style))
        content.append(Spacer(1, 10))
        
        # Low Priority
        content.append(Paragraph("Additional Context", ParagraphStyle(
            'Priority',
            parent=content_style,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica-Bold'
        )))
        if data.get('importance', {}).get('low'):
            for item in data['importance']['low']:
                content.append(Paragraph(f"• {item}", content_style))
        content.append(Spacer(1, 20))
        
        # Law Articles Section
        content.append(Paragraph("Relevant Indian Law Articles", section_style))
        if data.get('suggested_articles'):
            for article in data['suggested_articles']:
                content.append(Paragraph(
                    f"{article.get('article', '')} - {article.get('title', '')}",
                    ParagraphStyle(
                        'ArticleTitle',
                        parent=content_style,
                        textColor=colors.HexColor('#2c3e50'),
                        fontName='Helvetica-Bold'
                    )
                ))
                content.append(Paragraph(article.get('description', ''), content_style))
                content.append(Spacer(1, 10))
        else:
            content.append(Paragraph("No relevant law articles found.", content_style))
        
        # Build the PDF
        doc.build(content)
        return report_filename
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        return None

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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the document
        result = process_document(file_path)
        
        # Generate PDF report
        report_filename = generate_pdf_report(result, filename)
        if report_filename:
            result['report_url'] = f'/reports/{report_filename}'
        else:
            print("Warning: PDF report generation failed")
        
        # Clean up the uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return create_response(data=result)
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        return create_response(error=str(e), status=500)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True) 