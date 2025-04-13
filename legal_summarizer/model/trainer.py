import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
import torch
from typing import List, Dict
import json
import logging
import os
from database.models import TrainingData, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalSummarizerTrainer:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        output_dir: str = "trained_model",
        batch_size: int = 2,
        num_epochs: int = 3,
        learning_rate: float = 2e-5
    ):
        self.model_name = model_name
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.learning_rate = learning_rate
        
        # Force CPU usage
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        torch.set_default_device('cpu')
        
        # Initialize model and tokenizer
        logger.info(f"Loading model {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Set up training arguments with CPU configuration
        self.training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=4,
            weight_decay=0.01,
            logging_dir='./logs',
            learning_rate=learning_rate,
            do_train=True,
            do_eval=True,
            save_total_limit=3,
            no_cuda=True,  # Force CPU
            optim="adamw_torch",
            max_grad_norm=0.5,
            warmup_ratio=0.1,
            logging_steps=1
        )

    def _prepare_dataset(self, texts: List[str], summaries: List[str]) -> Dataset:
        """Prepare dataset for training"""
        logger.info("Preparing dataset...")
        encoded_data = []
        
        for text, summary in zip(texts, summaries):
            # Tokenize inputs with shorter sequences
            inputs = self.tokenizer(
                text,
                max_length=512,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            
            # Tokenize summaries
            labels = self.tokenizer(
                summary,
                max_length=128,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            
            encoded_data.append({
                'input_ids': inputs['input_ids'].squeeze(),
                'attention_mask': inputs['attention_mask'].squeeze(),
                'labels': labels['input_ids'].squeeze()
            })
        
        return Dataset.from_list(encoded_data)

    def load_training_data(self) -> tuple:
        """Load training data from database"""
        logger.info("Loading training data from database...")
        session = init_db()
        training_data = session.query(TrainingData).all()
        
        texts = [data.document_text for data in training_data]
        summaries = [data.summary for data in training_data]
        
        logger.info(f"Loaded {len(texts)} training examples")
        return texts, summaries

    def train(self, texts: List[str] = None, summaries: List[str] = None):
        """Train the model on provided data or load from database"""
        if texts is None or summaries is None:
            texts, summaries = self.load_training_data()
        
        if not texts or not summaries:
            raise ValueError("No training data available")
        
        dataset = self._prepare_dataset(texts, summaries)
        
        # Split dataset into train and validation
        train_size = int(0.9 * len(dataset))
        train_dataset = dataset.select(range(train_size))
        eval_dataset = dataset.select(range(train_size, len(dataset)))
        
        logger.info(f"Training set size: {len(train_dataset)}")
        logger.info(f"Validation set size: {len(eval_dataset)}")
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset
        )
        
        # Train the model
        logger.info("Starting training...")
        try:
            trainer.train()
            
            # Save the model
            logger.info(f"Saving model to {self.output_dir}")
            trainer.save_model()
            self.tokenizer.save_pretrained(self.output_dir)
            logger.info("Training completed!")
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            raise

    def evaluate(self, test_texts: List[str], test_summaries: List[str]) -> Dict:
        """Evaluate the model on test data"""
        logger.info("Evaluating model...")
        test_dataset = self._prepare_dataset(test_texts, test_summaries)
        
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            eval_dataset=test_dataset
        )
        
        metrics = trainer.evaluate()
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics

if __name__ == "__main__":
    # Example usage
    trainer = LegalSummarizerTrainer()
    
    # Train the model
    try:
        trainer.train()
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise 