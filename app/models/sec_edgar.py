"""
SEC EDGAR Database Models

Models for storing SEC (U.S. Securities and Exchange Commission) data:
- Company information (CIK, ticker, name)
- SEC filings (10-K, 10-Q, 8-K, etc.)
- Financial facts (XBRL data)

Author: AI Assistant
Created: 2025-11-22
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, DECIMAL, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class SECCompany(Base):
    """
    SEC Company Information

    Stores basic company information from SEC EDGAR database.

    CIK (Central Index Key) is SEC's unique identifier for companies.
    """
    __tablename__ = "sec_companies"

    id = Column(Integer, primary_key=True, index=True)

    # SEC Identifiers
    cik = Column(String(10), unique=True, nullable=False, index=True)  # 10-digit CIK
    ticker = Column(String(10), index=True)  # Stock ticker (can be null if delisted)
    company_name = Column(String(500), nullable=False)

    # Company Details
    sic = Column(String(10))  # Standard Industrial Classification
    sic_description = Column(String(200))
    category = Column(String(100))
    entity_type = Column(String(100))

    # Address
    business_address = Column(JSON)  # {street1, street2, city, state, zip, country}
    mailing_address = Column(JSON)

    # Contact
    phone = Column(String(50))
    website = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    former_names = Column(JSON)  # List of previous company names

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    filings = relationship("SECFiling", back_populates="company", cascade="all, delete-orphan")
    financial_facts = relationship("SECFinancialFact", back_populates="company", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_sec_company_ticker', 'ticker'),
        Index('idx_sec_company_name', 'company_name'),
        Index('idx_sec_company_sic', 'sic'),
    )

    def __repr__(self):
        return f"<SECCompany(cik={self.cik}, ticker={self.ticker}, name={self.company_name})>"


class SECFiling(Base):
    """
    SEC Filings

    Stores information about SEC filings (10-K, 10-Q, 8-K, etc.)

    Common Form Types:
    - 10-K: Annual report
    - 10-Q: Quarterly report
    - 8-K: Current report (material events)
    - DEF 14A: Proxy statement
    - 13F-HR: Institutional holdings
    - 4: Statement of changes in beneficial ownership
    """
    __tablename__ = "sec_filings"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    company_id = Column(Integer, ForeignKey('sec_companies.id'), nullable=False)

    # Filing Identifiers
    cik = Column(String(10), nullable=False, index=True)
    accession_number = Column(String(25), unique=True, nullable=False, index=True)  # Unique filing ID

    # Filing Details
    form_type = Column(String(20), nullable=False, index=True)  # 10-K, 10-Q, etc.
    filing_date = Column(Date, nullable=False, index=True)
    report_date = Column(Date)  # Period end date (for periodic reports)
    accepted_date = Column(DateTime)

    # Document Information
    primary_document = Column(String(255))  # Main document filename
    primary_doc_description = Column(String(500))
    document_url = Column(String(1000))  # Full URL to document

    # Filing Size
    size = Column(Integer)  # File size in bytes
    file_count = Column(Integer)  # Number of files in submission

    # Amendment Information
    is_amendment = Column(Boolean, default=False)
    is_xbrl = Column(Boolean, default=False)  # Has XBRL data

    # Metadata
    items = Column(JSON)  # List of item numbers (for 8-K, etc.)
    raw_data = Column(JSON)  # Full raw data from API

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("SECCompany", back_populates="filings")

    # Indexes
    __table_args__ = (
        Index('idx_sec_filing_company_form_date', 'company_id', 'form_type', 'filing_date'),
        Index('idx_sec_filing_cik_date', 'cik', 'filing_date'),
        Index('idx_sec_filing_form_date', 'form_type', 'filing_date'),
    )

    def __repr__(self):
        return f"<SECFiling(cik={self.cik}, form={self.form_type}, date={self.filing_date})>"


class SECFinancialFact(Base):
    """
    SEC Financial Facts (XBRL Data)

    Stores structured financial data extracted from XBRL-formatted filings.

    Common GAAP Concepts:
    - Revenue / Revenues
    - Assets / AssetsCurrent
    - Liabilities / LiabilitiesCurrent
    - NetIncomeLoss
    - EarningsPerShareBasic
    - StockholdersEquity
    """
    __tablename__ = "sec_financial_facts"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    company_id = Column(Integer, ForeignKey('sec_companies.id'), nullable=False)

    # Identifiers
    cik = Column(String(10), nullable=False, index=True)

    # XBRL Taxonomy
    taxonomy = Column(String(50), nullable=False)  # 'us-gaap', 'dei', 'srt', etc.
    concept = Column(String(200), nullable=False, index=True)  # 'Revenue', 'Assets', etc.
    label = Column(String(500))  # Human-readable label

    # Time Period
    end_date = Column(Date, nullable=False, index=True)  # Period end date
    start_date = Column(Date)  # Period start date (for duration metrics)
    fiscal_year = Column(Integer, index=True)
    fiscal_period = Column(String(10))  # 'FY', 'Q1', 'Q2', 'Q3', 'Q4'

    # Value
    value = Column(DECIMAL(20, 4))  # Numeric value
    unit = Column(String(20))  # 'USD', 'shares', etc.
    decimals = Column(Integer)  # Decimal precision

    # Form Reference
    form_type = Column(String(20))  # Source form (10-K, 10-Q, etc.)
    filing_date = Column(Date)
    accession_number = Column(String(25))

    # Frame Information
    frame = Column(String(50))  # 'CY2023Q4', 'CY2023', etc.

    # Metadata
    raw_data = Column(JSON)  # Full raw fact data

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("SECCompany", back_populates="financial_facts")

    # Indexes
    __table_args__ = (
        Index('idx_sec_fact_company_concept_date', 'company_id', 'concept', 'end_date'),
        Index('idx_sec_fact_cik_concept', 'cik', 'concept'),
        Index('idx_sec_fact_concept_date', 'concept', 'end_date'),
        Index('idx_sec_fact_fiscal_year', 'cik', 'fiscal_year'),
    )

    def __repr__(self):
        return f"<SECFinancialFact(cik={self.cik}, concept={self.concept}, value={self.value}, date={self.end_date})>"


class SECInstitutionalHolding(Base):
    """
    SEC Institutional Holdings (13F)

    Stores institutional investment manager holdings from 13F-HR filings.

    13F filings show what stocks institutional investors (like Buffett, Dalio)
    are holding at the end of each quarter.
    """
    __tablename__ = "sec_institutional_holdings"

    id = Column(Integer, primary_key=True, index=True)

    # Filing Information
    filer_cik = Column(String(10), nullable=False, index=True)  # Institution's CIK
    filer_name = Column(String(500), nullable=False)  # Institution name
    accession_number = Column(String(25), nullable=False)  # 13F filing accession number

    # Period
    report_date = Column(Date, nullable=False, index=True)  # Quarter end date
    filing_date = Column(Date)

    # Holding Information
    holding_company_name = Column(String(500), nullable=False)  # Company being held
    holding_ticker = Column(String(10), index=True)
    holding_cusip = Column(String(9), index=True)  # CUSIP identifier

    # Position Details
    shares = Column(DECIMAL(20, 4))  # Number of shares held
    value = Column(DECIMAL(20, 2))  # Position value in USD
    share_price = Column(DECIMAL(10, 4))  # Implied price per share

    # Position Type
    share_type = Column(String(20))  # 'SH-SOLE', 'SH-SHARED', 'SH-NONE'
    put_call = Column(String(10))  # 'Put', 'Call', or null

    # Change Information
    shares_change = Column(DECIMAL(20, 4))  # Change from previous quarter
    shares_change_pct = Column(DECIMAL(10, 4))  # Percentage change

    # Portfolio Information
    portfolio_weight = Column(DECIMAL(10, 6))  # % of total portfolio

    # Metadata
    raw_data = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_sec_holding_filer_date', 'filer_cik', 'report_date'),
        Index('idx_sec_holding_ticker_date', 'holding_ticker', 'report_date'),
        Index('idx_sec_holding_filer_ticker', 'filer_cik', 'holding_ticker'),
    )

    def __repr__(self):
        return f"<SECInstitutionalHolding(filer={self.filer_name}, holding={self.holding_company_name}, shares={self.shares})>"
