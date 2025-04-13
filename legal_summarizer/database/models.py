from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_text = Column(Text, nullable=False)
    summary = Column(Text)
    dates = Column(Text)  # Stored as JSON string
    importance_high = Column(Text)  # Stored as JSON string
    importance_medium = Column(Text)  # Stored as JSON string
    importance_low = Column(Text)  # Stored as JSON string
    processing_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrainingData(Base):
    __tablename__ = 'training_data'

    id = Column(Integer, primary_key=True)
    document_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(100))  # Source of the training data
    quality_score = Column(Float)  # Score for data quality
    created_at = Column(DateTime, default=datetime.utcnow)

# Database initialization
def init_db(db_url='sqlite:///legal_summarizer.db'):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session() 