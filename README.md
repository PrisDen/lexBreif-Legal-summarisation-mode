# LexBrief - Legal Document Summarization System

An AI-powered web application that automatically summarizes legal documents, extracts important dates, and classifies content by importance.

## Recent Updates

### Enhanced Text Processing
- Improved text formatting for better PDF readability
- Implemented smart text chunking with sentence boundary preservation
- Enhanced entity extraction with caching for better performance
- Added comprehensive error handling and logging

### PDF Generation Improvements
- Added proper spacing and formatting for legal documents
- Implemented section header formatting
- Enhanced paragraph indentation and line spacing
- Improved overall document structure and readability

### API and Documentation
- Added comprehensive API documentation
- Created detailed user guides
- Improved error handling and response formats
- Added test cases for core functionality

## Features

* Document Upload Support:  
   * PDF files  
   * DOCX (Word) files  
   * TXT files
* AI-Powered Analysis:  
   * Document summarization using transformer models  
   * Important dates extraction  
   * Content classification by importance level
* Interactive UI:  
   * Drag-and-drop file upload  
   * Real-time processing feedback  
   * Tabbed interface for viewing results
* PDF Report Generation:  
   * Professional formatted reports  
   * Downloadable summaries  
   * Organized by importance

## Tech Stack

* Backend:  
   * Python/Flask  
   * Hugging Face Transformers  
   * PyPDF2 for PDF processing  
   * python-docx for DOCX processing
* Frontend:  
   * HTML5/CSS3  
   * JavaScript (Vanilla)  
   * Font Awesome icons
* Document Processing:  
   * Natural Language Processing  
   * Regular Expressions for date extraction  
   * ReportLab for PDF generation

## Setup

1. Clone the repository:
```bash
git clone https://github.com/PrisDen/lexBreif-Legal-summarisation-mode.git
cd lexBreif-Legal-summarisation-mode
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
cd legal_summarizer
flask run
```

5. Open your browser and navigate to `http://127.0.0.1:5001`

## Usage

1. Upload a legal document using either:  
   * Drag and drop into the upload area  
   * Click the "Choose File" button
2. Wait for the AI to process your document
3. View the results:  
   * Document summary  
   * Important dates  
   * Content classified by importance
4. Download the generated PDF report

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

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

## Acknowledgments

- Hugging Face Transformers
- spaCy
- Flask
- ReportLab
