import os
import json
import requests
import logging
from tqdm import tqdm
from typing import List, Dict
import pandas as pd
from datasets import load_dataset, Dataset
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import init_db, TrainingData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDatasetPreparer:
    def __init__(self, output_dir: str = "legal_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.session = init_db()

    def download_indian_kanoon(self):
        """
        Download and process Indian legal cases from Indian Kanoon
        Note: This is a sample implementation. In production, you would need proper API access.
        """
        logger.info("Downloading Indian Kanoon dataset...")
        # This would typically use the Indian Kanoon API
        # For now, we'll use a sample of pre-processed cases
        sample_cases = [
            {
                "text": "IN THE SUPREME COURT OF INDIA CIVIL APPELLATE JURISDICTION CIVIL APPEAL NO.1234 OF 2024 [ARISING OUT OF SLP(C) NO.567 OF 2023] ...",
                "summary": "Supreme Court appeal regarding property dispute between siblings over ancestral property. Court upheld equal distribution among heirs."
            },
            # Add more sample cases
        ]
        return sample_cases

    def prepare_contract_dataset(self):
        """
        Prepare dataset from legal contracts
        """
        logger.info("Preparing contract dataset...")
        contracts = [
            {
                "text": """EMPLOYMENT AGREEMENT
                THIS AGREEMENT made as of the 15th day of March, 2024
                BETWEEN:
                ABC Corporation, a company incorporated under the laws of [State]
                (hereinafter referred to as the "Employer")
                AND:
                John Doe, of the City of [City]
                (hereinafter referred to as the "Employee")
                WHEREAS the Employer desires to obtain the benefit of the services of the Employee, and the Employee desires to render such services on the terms and conditions set forth...""",
                "summary": "Employment agreement between ABC Corporation and John Doe dated March 15, 2024, outlining terms of employment including duties, compensation, and termination conditions."
            },
            # Add more sample contracts
        ]
        return contracts

    def prepare_case_law_dataset(self):
        """
        Prepare dataset from case law documents
        """
        logger.info("Preparing case law dataset...")
        cases = [
            {
                "text": """SUPREME COURT OF THE UNITED STATES
                No. 20-1234
                JOHN DOE, PETITIONER v. JANE SMITH
                ON WRIT OF CERTIORARI TO THE UNITED STATES COURT OF
                APPEALS FOR THE NINTH CIRCUIT
                [March 15, 2024]
                Justice Roberts delivered the opinion of the Court.
                This case presents the question whether...""",
                "summary": "Supreme Court case between John Doe and Jane Smith regarding intellectual property rights in digital media. Court established new precedent for online content ownership."
            },
            # Add more sample cases
        ]
        return cases

    def save_to_database(self, documents: List[Dict]):
        """
        Save the prepared documents to the database
        """
        logger.info(f"Saving {len(documents)} documents to database...")
        for doc in tqdm(documents):
            training_data = TrainingData(
                document_text=doc['text'],
                summary=doc['summary'],
                source='legal_dataset',
                quality_score=1.0
            )
            self.session.add(training_data)
        
        self.session.commit()
        logger.info("Successfully saved to database")

    def prepare_dataset(self):
        """
        Prepare the complete legal dataset
        """
        all_documents = []
        
        # Collect documents from different sources
        all_documents.extend(self.download_indian_kanoon())
        all_documents.extend(self.prepare_contract_dataset())
        all_documents.extend(self.prepare_case_law_dataset())
        
        # Save to database
        self.save_to_database(all_documents)
        
        # Also save as JSON for backup
        output_file = os.path.join(self.output_dir, "legal_dataset.json")
        with open(output_file, 'w') as f:
            json.dump(all_documents, f, indent=2)
        
        logger.info(f"Dataset saved to {output_file}")
        return len(all_documents)

def main():
    try:
        preparer = LegalDatasetPreparer()
        num_documents = preparer.prepare_dataset()
        logger.info(f"Successfully prepared dataset with {num_documents} documents")
    except Exception as e:
        logger.error(f"Error preparing dataset: {str(e)}")

if __name__ == "__main__":
    main() 