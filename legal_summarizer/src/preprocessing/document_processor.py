import os
from typing import List, Dict, Union
import PyPDF2
from docx import Document
import spacy
from datetime import datetime
import re

class DocumentProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
    def process_document(self, file_path: str) -> Dict[str, Union[str, List[str]]]:
        """
        Process a document based on its file extension and return extracted text.
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            Dict containing:
                - text: Extracted text
                - dates: List of dates found
                - entities: List of named entities
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self._process_pdf(file_path)
        elif file_ext == '.docx':
            text = self._process_docx(file_path)
        elif file_ext == '.txt':
            text = self._process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
        # Process the extracted text
        doc = self.nlp(text)
        
        # Extract dates and entities
        dates = self._extract_dates(doc)
        entities = self._extract_entities(doc)
        
        return {
            'text': text,
            'dates': dates,
            'entities': entities
        }
    
    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def _process_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def _process_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_dates(self, doc) -> List[str]:
        """Extract dates from the document."""
        dates = []
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                dates.append(ent.text)
        return dates
    
    def _extract_entities(self, doc) -> List[Dict[str, str]]:
        """Extract named entities from the document."""
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        return entities 