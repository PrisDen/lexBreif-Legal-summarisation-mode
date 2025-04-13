import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import logging
from typing import List, Dict
import json
from database.models import TrainingData, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalSummarizerTester:
    def __init__(self, model_dir: str = "trained_model"):
        self.model_dir = model_dir
        
        # Load model and tokenizer
        logger.info(f"Loading model from {model_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        self.model.eval()  # Set to evaluation mode
        
        # Force CPU usage
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        torch.set_default_device('cpu')

    def generate_summary(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Generate a summary for the given legal text"""
        # Tokenize input text
        inputs = self.tokenizer(
            text,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Generate summary
        summary_ids = self.model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=max_length,
            min_length=min_length,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        
        # Decode summary
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def load_test_cases(self) -> List[Dict]:
        """Load some test cases from the database"""
        session = init_db()
        test_cases = session.query(TrainingData).limit(5).all()
        return [{"text": case.document_text, "reference_summary": case.summary} for case in test_cases]

    def evaluate_model(self):
        """Evaluate the model on test cases"""
        test_cases = self.load_test_cases()
        logger.info(f"Evaluating model on {len(test_cases)} test cases...")
        
        results = []
        for i, case in enumerate(test_cases, 1):
            logger.info(f"\nTest Case {i}:")
            logger.info("-" * 50)
            logger.info(f"Original Text (first 200 chars): {case['text'][:200]}...")
            logger.info(f"Reference Summary: {case['reference_summary']}")
            
            # Generate summary
            generated_summary = self.generate_summary(case['text'])
            logger.info(f"Generated Summary: {generated_summary}")
            
            results.append({
                "test_case": i,
                "original_text": case['text'],
                "reference_summary": case['reference_summary'],
                "generated_summary": generated_summary
            })
        
        # Save results
        output_dir = "test_results"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "model_test_results.json")
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\nTest results saved to {output_file}")
        return results

def main():
    try:
        tester = LegalSummarizerTester()
        tester.evaluate_model()
    except Exception as e:
        logger.error(f"Testing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 