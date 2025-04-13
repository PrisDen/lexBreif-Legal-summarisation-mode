import json
import random
from datetime import datetime, timedelta
import os
from typing import List, Dict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import init_db, TrainingData

# Templates for generating synthetic legal documents
AGREEMENT_TEMPLATES = [
    {
        "type": "Employment Agreement",
        "template": """EMPLOYMENT AGREEMENT

THIS AGREEMENT made as of the {date}

BETWEEN:
{company_name} ("Employer")
AND
{employee_name} ("Employee")

WHEREAS the Employer desires to employ the Employee and the Employee desires to accept such employment;

NOW THEREFORE in consideration of the mutual covenants and agreements herein contained, the parties agree as follows:

1. POSITION AND DUTIES
The Employee shall serve as {position} and shall perform such duties as are regularly and customarily performed by a person holding such position.

2. COMPENSATION
The Employer shall pay the Employee a base salary of {salary} per annum, payable in accordance with the Employer's standard payroll practices.

3. TERM
This Agreement shall commence on {start_date} and continue unless terminated in accordance with Section 4.

4. TERMINATION
Either party may terminate this Agreement upon providing {notice_period} days written notice to the other party.""",
        "summary_template": "Employment agreement between {company_name} and {employee_name} for the position of {position}, with a salary of {salary} per annum, commencing {start_date}, requiring {notice_period} days notice for termination."
    },
    {
        "type": "Non-Disclosure Agreement",
        "template": """NON-DISCLOSURE AGREEMENT

THIS AGREEMENT is made on {date}

BETWEEN:
{company_name} ("Disclosing Party")
AND
{recipient_name} ("Receiving Party")

1. CONFIDENTIAL INFORMATION
The Receiving Party agrees to maintain in confidence and not disclose any proprietary information received from the Disclosing Party.

2. TERM
This obligation of confidentiality shall remain in effect for {duration} years from the date of disclosure.

3. PERMITTED USE
The Receiving Party shall use the Confidential Information solely for the purpose of {purpose}.""",
        "summary_template": "Non-disclosure agreement between {company_name} and {recipient_name}, protecting confidential information for {duration} years, for the purpose of {purpose}."
    }
]

# Data for generating random content
COMPANIES = [
    "Tech Solutions Inc.", "Global Industries Ltd.", "Innovation Corp.",
    "Strategic Systems LLC", "Advanced Technologies Co.", "Premier Services Group"
]

NAMES = [
    "John Smith", "Emma Johnson", "Michael Brown", "Sarah Davis",
    "David Wilson", "Lisa Anderson", "Robert Taylor", "Jennifer Martinez"
]

POSITIONS = [
    "Software Engineer", "Project Manager", "Chief Technology Officer",
    "Product Manager", "Senior Developer", "Systems Architect"
]

PURPOSES = [
    "evaluating potential business collaboration",
    "developing joint technology solutions",
    "exploring strategic partnership opportunities",
    "conducting due diligence for potential acquisition"
]

def generate_random_date(start_year: int = 2024, end_year: int = 2025) -> str:
    """Generate a random date between start_year and end_year"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime("%d %B, %Y")

def generate_synthetic_document() -> Dict:
    """Generate a synthetic legal document"""
    template = random.choice(AGREEMENT_TEMPLATES)
    
    # Generate random values
    company = random.choice(COMPANIES)
    name = random.choice(NAMES)
    position = random.choice(POSITIONS)
    salary = f"${random.randint(80, 200)},000"
    notice_period = random.choice([30, 60, 90])
    duration = random.choice([2, 3, 5])
    purpose = random.choice(PURPOSES)
    date = generate_random_date()
    start_date = generate_random_date()
    
    # Fill template
    text = template["template"].format(
        date=date,
        company_name=company,
        employee_name=name,
        position=position,
        salary=salary,
        start_date=start_date,
        notice_period=notice_period,
        recipient_name=random.choice(NAMES),
        duration=duration,
        purpose=purpose
    )
    
    summary = template["summary_template"].format(
        company_name=company,
        employee_name=name,
        position=position,
        salary=salary,
        start_date=start_date,
        notice_period=notice_period,
        recipient_name=random.choice(NAMES),
        duration=duration,
        purpose=purpose
    )
    
    return {
        "text": text,
        "summary": summary,
        "type": template["type"]
    }

def generate_dataset(num_documents: int = 100) -> List[Dict]:
    """Generate a dataset of synthetic legal documents"""
    return [generate_synthetic_document() for _ in range(num_documents)]

def save_to_database(documents: List[Dict]) -> None:
    """Save generated documents to database"""
    session = init_db()
    
    for doc in documents:
        training_data = TrainingData(
            document_text=doc['text'],
            summary=doc['summary'],
            source='synthetic',
            quality_score=1.0
        )
        session.add(training_data)
    
    session.commit()
    session.close()

def main():
    # Generate synthetic documents
    num_documents = 100
    print(f"Generating {num_documents} synthetic legal documents...")
    documents = generate_dataset(num_documents)
    
    # Save to JSON file
    output_dir = "legal_data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "synthetic_legal_documents.json")
    
    with open(output_file, 'w') as f:
        json.dump(documents, f, indent=2)
    
    print(f"Saved synthetic documents to {output_file}")
    
    # Save to database
    print("Saving documents to database...")
    save_to_database(documents)
    print("Done!")

if __name__ == "__main__":
    main() 