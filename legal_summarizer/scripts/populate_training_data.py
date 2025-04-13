import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db, TrainingData
import json
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_json_data(file_path: str) -> List[Dict]:
    """Load training data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def populate_database(data: List[Dict], session) -> None:
    """Populate database with training data"""
    for item in data:
        training_data = TrainingData(
            document_text=item['text'],
            summary=item['summary'],
            source=item.get('source', 'manual'),
            quality_score=item.get('quality_score', 1.0)
        )
        session.add(training_data)
    
    session.commit()
    logger.info(f"Added {len(data)} training examples to database")

def main():
    # Initialize database
    session = init_db()
    
    # Sample training data (you would typically load this from a file)
    sample_data = [
        {
            "text": "This Agreement is made on January 15, 2024, between ABC Corp ('Seller') and XYZ Ltd ('Buyer'). The Seller agrees to sell and the Buyer agrees to purchase 1000 units of Product A at $50 per unit. Delivery shall be made within 30 days of this agreement. Payment terms are net 60 days.",
            "summary": "Sales agreement between ABC Corp and XYZ Ltd for 1000 units of Product A at $50/unit, with 30-day delivery and 60-day payment terms.",
            "source": "sample",
            "quality_score": 1.0
        },
        {
            "text": "Notice is hereby given that a meeting of the Board of Directors of ABC Corporation will be held at the company's headquarters on March 1, 2024, at 10:00 AM. The agenda includes: 1. Review of Q4 2023 financial results 2. Discussion of expansion plans 3. Appointment of new CFO.",
            "summary": "Board meeting notice for ABC Corporation on March 1, 2024, covering Q4 2023 results, expansion plans, and CFO appointment.",
            "source": "sample",
            "quality_score": 1.0
        }
    ]
    
    try:
        # Check if JSON file exists with more training data
        if os.path.exists('training_data.json'):
            logger.info("Loading training data from JSON file...")
            data = load_json_data('training_data.json')
        else:
            logger.info("Using sample training data...")
            data = sample_data
        
        # Populate database
        populate_database(data, session)
        logger.info("Database population completed successfully")
        
    except Exception as e:
        logger.error(f"Error populating database: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main() 