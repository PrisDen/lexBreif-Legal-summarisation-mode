from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from typing import Dict, List, Tuple
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize

class LegalSummarizer:
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize the legal document summarizer.
        
        Args:
            model_name (str): Name of the pre-trained model to use
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.summarizer = pipeline("summarization", model=model_name, tokenizer=self.tokenizer)
        
    def summarize(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Generate a summary of the input text.
        
        Args:
            text (str): Input text to summarize
            max_length (int): Maximum length of the summary
            min_length (int): Minimum length of the summary
            
        Returns:
            str: Generated summary
        """
        # Split text into chunks if it's too long
        chunks = self._chunk_text(text)
        
        summaries = []
        for chunk in chunks:
            summary = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            summaries.append(summary[0]['summary_text'])
            
        return " ".join(summaries)
    
    def categorize_importance(self, text: str) -> Dict[str, List[str]]:
        """
        Categorize sentences based on their importance.
        
        Args:
            text (str): Input text to categorize
            
        Returns:
            Dict containing lists of sentences categorized by importance
        """
        sentences = sent_tokenize(text)
        
        # Calculate sentence importance using TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
        
        # Normalize scores
        normalized_scores = (sentence_scores - sentence_scores.min()) / (sentence_scores.max() - sentence_scores.min())
        
        # Categorize sentences
        very_important = []
        important = []
        not_so_important = []
        
        for i, score in enumerate(normalized_scores):
            if score > 0.7:
                very_important.append(sentences[i])
            elif score > 0.4:
                important.append(sentences[i])
            else:
                not_so_important.append(sentences[i])
                
        return {
            'very_important': very_important,
            'important': important,
            'not_so_important': not_so_important
        }
    
    def _chunk_text(self, text: str, chunk_size: int = 1024) -> List[str]:
        """
        Split text into chunks of appropriate size for the model.
        
        Args:
            text (str): Input text
            chunk_size (int): Maximum size of each chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += 1
            
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks 