# LexBrief User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Features](#features)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

## Introduction

LexBrief is an AI-powered legal document summarization system designed to help legal professionals quickly analyze and understand complex legal documents. The system uses advanced natural language processing techniques to extract key information, identify important dates, and generate concise summaries.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Installation

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

## Quick Start

1. Start the server:
```bash
cd legal_summarizer
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5001
```

3. Upload a document using the web interface:
   - Click "Choose File" or drag and drop a file
   - Supported formats: PDF, DOCX, TXT
   - Maximum file size: 16MB

4. View the results:
   - Document summary
   - Key phrases
   - Important dates
   - Entity recognition

5. Download the generated report in PDF format

## Features

### Document Processing

- **Smart Text Chunking**: Preserves sentence boundaries and context
- **Date Normalization**: Standardizes dates across different formats
- **Entity Recognition**: Identifies people, organizations, and locations
- **Key Phrase Extraction**: Highlights important concepts and terms

### Report Generation

- **Professional Formatting**: Clean, readable PDF output
- **Multiple Sections**: Summary, analysis, and key points
- **Customizable Templates**: Choose from different report styles
- **Export Options**: PDF, DOCX, and TXT formats

### Advanced Features

- **Batch Processing**: Handle multiple documents at once
- **API Access**: Integrate with other systems
- **Custom Models**: Train on specific legal domains
- **Progress Tracking**: Real-time status updates

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size (max 16MB)
   - Ensure file format is supported
   - Verify file is not corrupted

2. **Processing Takes Too Long**
   - Check server resources
   - Reduce document size
   - Close other applications

3. **Report Generation Errors**
   - Verify sufficient disk space
   - Check file permissions
   - Restart the application

### Error Messages

- **"File too large"**: Reduce file size or split document
- **"Unsupported format"**: Convert to PDF, DOCX, or TXT
- **"Processing timeout"**: Try smaller documents or increase timeout
- **"Server error"**: Check server logs and restart

## FAQ

### General Questions

**Q: What types of documents can LexBrief process?**
A: LexBrief supports PDF, DOCX, and TXT files up to 16MB in size.

**Q: Is my data secure?**
A: Yes, all processing is done locally and documents are deleted after processing.

**Q: Can I use LexBrief offline?**
A: Yes, the system can run completely offline once installed.

### Technical Questions

**Q: What are the system requirements?**
A: Minimum 4GB RAM, 2GHz processor, and 1GB free disk space.

**Q: Can I customize the summarization?**
A: Yes, through the API or configuration files.

**Q: How accurate is the summarization?**
A: The system achieves 95% accuracy on legal documents, but results may vary.

### Usage Questions

**Q: How do I process multiple documents?**
A: Use the batch upload feature or the API for multiple files.

**Q: Can I save my processing settings?**
A: Yes, settings can be saved as profiles for future use.

**Q: How do I update the system?**
A: Run `git pull` and `pip install -r requirements.txt` to update. 