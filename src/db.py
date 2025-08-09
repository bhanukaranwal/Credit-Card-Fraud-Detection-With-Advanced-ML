from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/frauddb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    features = Column(JSON, nullable=False)
    true_label = Column(Integer, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class PredictionLog(Base):
    __tablename__ = "prediction_log"
    id = Column(Integer, primary_key=True, index=True)
    features = Column(JSON, nullable=False)
    predicted_label = Column(Integer, nullable=False)
    predicted_prob = Column(Float, nullable=False)
    prediction_time = Column(DateTime, default=datetime.utcnow)

class ComplianceReport(Base):
    __tablename__ = "compliance_report"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    author = Column(String, nullable=False)
    report_name = Column(String)
    report_file = Column(LargeBinary)  # PDF blob
    fairness_gaps = Column(JSON)
    model_version = Column(Integer)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
