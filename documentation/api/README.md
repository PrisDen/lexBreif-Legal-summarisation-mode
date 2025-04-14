# LexBrief API Documentation

## Overview

The LexBrief API provides endpoints for legal document processing, summarization, and analysis. All endpoints return JSON responses.

## Base URL

```
http://localhost:5001
```

## Authentication

Currently, the API does not require authentication. Future versions will implement OAuth2.

## Endpoints

### Health Check

```
GET /health
```

Check if the server is running.

**Response**
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

### Document Processing

```
POST /summarize
```

Process and summarize a legal document.

**Request**
- Content-Type: multipart/form-data
- Body:
  - `file`: The document file (PDF, DOCX, or TXT)

**Response**
```json
{
    "status": "success",
    "message": "Document processed successfully",
    "data": {
        "summary": "Document summary text...",
        "key_phrases": ["phrase1", "phrase2"],
        "entities": {
            "dates": ["2023-01-01"],
            "people": ["John Doe"],
            "organizations": ["Supreme Court"]
        },
        "report_url": "/reports/summary_20230414_123456.pdf"
    }
}
```

### Report Download

```
GET /reports/{filename}
```

Download a generated report.

**Response**
- Content-Type: application/pdf
- Body: PDF file content

## Error Handling

All error responses follow this format:

```json
{
    "status": "error",
    "message": "Error description",
    "code": 400
}
```

Common error codes:
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

Current rate limits:
- 100 requests per hour
- 10 concurrent requests

## Examples

### Python

```python
import requests

# Upload and process document
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:5001/summarize', files=files)
print(response.json())

# Download report
report_url = response.json()['data']['report_url']
report = requests.get(f'http://localhost:5001{report_url}')
with open('summary.pdf', 'wb') as f:
    f.write(report.content)
```

### JavaScript

```javascript
// Upload and process document
const formData = new FormData();
formData.append('file', documentFile);

fetch('http://localhost:5001/summarize', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(data);
    // Download report
    window.location.href = `http://localhost:5001${data.data.report_url}`;
});
``` 