"""
LLM Analysis Tracking Models
Track LLM agent analyses and performance
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from app.database.session import Base


class LLMAnalysis(Base):
    """
    LLM Analysis Record
    
    Stores individual LLM agent analysis results
    """
    __tablename__ = "llm_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Request Info
    stock_code = Column(String(10), index=True, nullable=False)
    stock_name = Column(String(100))
    analysis_type = Column(String(50), index=True)  # 'news_risk', 'combined_signal', 'explanation'
    
    # LLM Info
    llm_model = Column(String(50), index=True, nullable=False)  # 'claude', 'gpt4', 'gemini', 'grok'
    model_version = Column(String(50))  # e.g., 'claude-sonnet-4-20250514'
    
    # Input Data
    input_data = Column(JSON)  # All data sent to LLM
    
    # Output
    llm_response = Column(Text)  # Raw LLM response
    parsed_result = Column(JSON)  # Structured result
    
    # Decision (for signal analysis)
    decision = Column(String(20))  # 'BUY', 'SELL', 'HOLD'
    confidence = Column(Float)  # 0-100
    
    # Performance Metrics
    tokens_used = Column(Integer)
    cost = Column(Float)  # In USD
    latency_ms = Column(Integer)  # Response time in milliseconds
    
    # Metadata
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<LLMAnalysis {self.llm_model} for {self.stock_code} at {self.created_at}>"


class LLMConsensus(Base):
    """
    LLM Consensus Result
    
    Stores aggregated results from multiple LLMs
    """
    __tablename__ = "llm_consensus"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Request Info
    stock_code = Column(String(10), index=True, nullable=False)
    stock_name = Column(String(100))
    analysis_type = Column(String(50), index=True)
    
    # Individual Results
    claude_analysis_id = Column(Integer)  # FK to llm_analyses
    gpt4_analysis_id = Column(Integer)
    gemini_analysis_id = Column(Integer)
    grok_analysis_id = Column(Integer)
    
    # Votes
    buy_votes = Column(Integer, default=0)
    sell_votes = Column(Integer, default=0)
    hold_votes = Column(Integer, default=0)
    
    # Consensus Decision
    consensus_decision = Column(String(20))  # 'BUY', 'SELL', 'HOLD', 'NO_CONSENSUS'
    consensus_confidence = Column(Float)  # 0-100
    agreement_level = Column(Float)  # 0-1 (how many models agreed)
    
    # Average Metrics
    avg_confidence = Column(Float)
    total_cost = Column(Float)
    total_latency_ms = Column(Integer)
    
    # Final Recommendation
    recommendation = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<LLMConsensus {self.consensus_decision} for {self.stock_code} at {self.created_at}>"


class LLMPerformance(Base):
    """
    LLM Performance Tracking
    
    Aggregated performance metrics per model
    """
    __tablename__ = "llm_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model Info
    llm_model = Column(String(50), index=True, nullable=False, unique=True)
    
    # Usage Stats
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Performance Stats
    avg_latency_ms = Column(Float)
    success_rate = Column(Float)  # 0-1
    
    # Accuracy Metrics (require ground truth)
    correct_predictions = Column(Integer, default=0)
    total_predictions = Column(Integer, default=0)
    accuracy = Column(Float)  # 0-1
    
    # Decision Breakdown
    buy_count = Column(Integer, default=0)
    sell_count = Column(Integer, default=0)
    hold_count = Column(Integer, default=0)
    
    # Timestamps
    last_used_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LLMPerformance {self.llm_model}: {self.total_requests} requests, {self.accuracy:.2%} accuracy>"


class DataCollectionLog(Base):
    """
    Data Collection Log
    
    Track all data collection activities
    """
    __tablename__ = "data_collection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Collection Info
    collector_type = Column(String(50), index=True, nullable=False)  # 'kis', 'yahoo', 'dart', 'news'
    action = Column(String(100))  # 'collect_price', 'collect_news', etc.
    
    # Target
    target_code = Column(String(20), index=True)  # Stock code or index symbol
    target_name = Column(String(100))
    
    # Result
    success = Column(Boolean, default=True)
    records_collected = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Metadata
    metadata = Column(JSON)  # Additional info
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<DataCollectionLog {self.collector_type} for {self.target_code} at {self.created_at}>"
