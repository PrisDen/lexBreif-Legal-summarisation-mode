import os
import json
import requests
import logging
from tqdm import tqdm
from typing import List, Dict
import pandas as pd
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDocumentDownloader:
    def __init__(self, output_dir: str = "legal_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def download_supreme_court_judgments(self):
        """
        Download Supreme Court judgments from the Supreme Court of India website
        Note: This is a demonstration. In production, you should respect the website's robots.txt
        """
        base_url = "https://main.sci.gov.in/judgments"
        logger.info("Downloading Supreme Court judgments...")
        
        try:
            # Create a list to store documents
            documents = []
            
            # In production, you would implement proper pagination and crawling
            # This is a simplified version for demonstration
            response = requests.get(base_url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract judgment links and details
                # Implementation would depend on the actual website structure
                
                # Save the data
                output_file = os.path.join(self.output_dir, "supreme_court_judgments.json")
                with open(output_file, 'w') as f:
                    json.dump(documents, f, indent=2)
                
                logger.info(f"Saved {len(documents)} Supreme Court judgments")
                return documents
            else:
                logger.error(f"Failed to download Supreme Court judgments: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error downloading Supreme Court judgments: {str(e)}")
            return []

    def download_legal_contracts(self):
        """
        Download sample legal contracts from public sources
        """
        logger.info("Downloading legal contracts...")
        
        # Sources of legal contracts (these would be real URLs in production)
        contract_sources = [
            "https://example.com/legal-contracts/employment",
            "https://example.com/legal-contracts/nda",
            "https://example.com/legal-contracts/service-agreement"
        ]
        
        documents = []
        for source in contract_sources:
            try:
                # In production, implement proper rate limiting and error handling
                time.sleep(1)  # Basic rate limiting
                # Implementation would depend on the actual source structure
                
                # Add processed document to the list
                documents.append({
                    "text": "Contract text would go here",
                    "summary": "Contract summary would go here",
                    "source": source
                })
            except Exception as e:
                logger.error(f"Error downloading from {source}: {str(e)}")
        
        return documents

    def clean_text(self, text: str) -> str:
        """Clean and normalize legal text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep legal citations
        text = re.sub(r'[^\w\s\.\,\-\(\)\[\]\d\/]', '', text)
        return text.strip()

    def extract_summary(self, text: str) -> str:
        """
        Extract a summary from the legal document
        In production, you would implement a more sophisticated approach
        """
        # Find the first paragraph after keywords like "ORDER" or "JUDGMENT"
        summary_markers = ["ORDER", "JUDGMENT", "HELD:", "Therefore,"]
        lines = text.split('\n')
        
        for marker in summary_markers:
            try:
                marker_index = next(i for i, line in enumerate(lines) if marker in line.upper())
                summary_text = ' '.join(lines[marker_index:marker_index + 3])
                return self.clean_text(summary_text)
            except StopIteration:
                continue
        
        # If no marker found, take the first and last paragraph
        return self.clean_text(lines[0] + " ... " + lines[-1])

    def download_and_process(self):
        """
        Download and process legal documents from all sources
        """
        all_documents = []
        
        # Download from different sources
        supreme_court_docs = self.download_supreme_court_judgments()
        contract_docs = self.download_legal_contracts()
        
        all_documents.extend(supreme_court_docs)
        all_documents.extend(contract_docs)
        
        # Save all documents
        output_file = os.path.join(self.output_dir, "all_legal_documents.json")
        with open(output_file, 'w') as f:
            json.dump(all_documents, f, indent=2)
        
        logger.info(f"Downloaded and processed {len(all_documents)} documents")
        return all_documents

def main():
    try:
        downloader = LegalDocumentDownloader()
        documents = downloader.download_and_process()
        logger.info(f"Successfully downloaded {len(documents)} legal documents")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 