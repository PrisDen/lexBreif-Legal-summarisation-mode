# LexBrief: AI-Powered Legal Document Summarization System

LexBrief is an advanced legal document summarization system that leverages state-of-the-art transformer models and specialized text processing techniques to automatically analyze and summarize legal documents.

## Features

- Intelligent text processing with sentence boundary preservation
- Advanced date normalization with context awareness
- Entity recognition for legal terminology
- Enhanced PDF generation with improved readability
- RESTful API for document processing
- Real-time processing status updates
- Multiple export formats (PDF, DOCX, TXT)

## Project Structure

```
lexBrief-Legal-summarisation-mode/
├── legal_summarizer/          # Main application code
│   ├── app.py                # Flask application
│   ├── models/               # ML models and processing
│   ├── utils/                # Utility functions
│   ├── static/               # Static files (CSS, JS)
│   └── templates/            # HTML templates
├── documentation/            # Documentation
│   ├── research_paper/      # Research paper and diagrams
│   ├── api/                 # API documentation
│   └── user_guides/         # User guides
├── tests/                   # Test files
├── requirements.txt         # Dependencies
└── README.md               # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lexBrief-Legal-summarisation-mode.git
cd lexBrief-Legal-summarisation-mode
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
cd legal_summarizer
python app.py
```

2. Access the web interface at `http://localhost:5001`

3. Upload documents through the web interface or API

## API Documentation

### Endpoints

- `POST /summarize`: Process and summarize a document
- `GET /reports/{filename}`: Download generated reports
- `GET /health`: Check server status

### Example API Usage

```python
import requests

# Upload and process document
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:5001/summarize', files=files)
print(response.json())

# Download generated report
report_url = response.json()['report_url']
report = requests.get(report_url)
with open('summary.pdf', 'wb') as f:
    f.write(report.content)
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 style guidelines. Use flake8 for linting:
```bash
flake8 legal_summarizer/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hugging Face Transformers
- spaCy
- Flask
- ReportLab
