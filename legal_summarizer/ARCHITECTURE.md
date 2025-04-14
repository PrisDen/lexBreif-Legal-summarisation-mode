# LexBrief Technical Architecture

This document provides a detailed explanation of each component in the LexBrief legal document summarization system.

## Directory Structure Overview

### 1. Main Application Components

#### `app.py`
- **Purpose**: Main Flask application entry point
- **Key Features**:
  - RESTful API endpoints
  - File upload handling
  - PDF report generation
  - Error handling
- **Technical Details**:
  - Uses Flask for web framework
  - Implements CORS for cross-origin requests
  - Handles multipart form data for file uploads
  - Uses ReportLab for PDF generation

#### `utils/text_processors.py`
- **Purpose**: Core text processing functionality
- **Key Components**:
  - TextProcessor class with optimized methods
  - Caching mechanisms for performance
  - Smart text chunking
  - Entity extraction
- **Technical Details**:
  - Uses LRU caching for repeated operations
  - Implements regex patterns for entity extraction
  - Uses spaCy for NLP tasks
  - Type hints for better code maintainability

#### `config/config.py`
- **Purpose**: Configuration management
- **Features**:
  - Environment variable handling
  - Application settings
  - Path configurations
- **Technical Details**:
  - Uses Python's pathlib for path handling
  - Implements environment variable fallbacks
  - Type-safe configuration values

For more details, see the full documentation in the root directory. 