import os
import json
from datetime import datetime
from typing import Dict, Any
from preprocessing.document_processor import DocumentProcessor
from model.summarizer import LegalSummarizer

class LegalDocumentSummarizer:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.summarizer = LegalSummarizer()
        
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a legal document and generate a comprehensive summary.
        
        Args:
            file_path (str): Path to the legal document
            
        Returns:
            Dict containing the processed results
        """
        # Process the document
        processed_data = self.document_processor.process_document(file_path)
        
        # Generate summary
        summary = self.summarizer.summarize(processed_data['text'])
        
        # Categorize information
        categorized_info = self.summarizer.categorize_importance(processed_data['text'])
        
        # Prepare the final report
        report = {
            'document_info': {
                'filename': os.path.basename(file_path),
                'processing_date': datetime.now().isoformat(),
                'total_pages': len(processed_data['text'].split('\n')) // 50  # Approximate page count
            },
            'key_dates': processed_data['dates'],
            'important_entities': processed_data['entities'],
            'summary': summary,
            'categorized_information': categorized_info
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_path: str):
        """
        Save the generated report to a file.
        
        Args:
            report (Dict): The report to save
            output_path (str): Path where to save the report
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

def main():
    # Example usage
    summarizer = LegalDocumentSummarizer()
    
    # Process a document
    input_file = "path/to/legal/document.pdf"  # Replace with actual file path
    output_file = "output/summary.json"  # Replace with desired output path
    
    try:
        report = summarizer.process_document(input_file)
        summarizer.save_report(report, output_file)
        print(f"Summary generated successfully and saved to {output_file}")
    except Exception as e:
        print(f"Error processing document: {str(e)}")

if __name__ == "__main__":
    main() 