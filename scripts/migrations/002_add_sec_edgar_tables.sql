-- ============================================================================
-- Database Migration: SEC EDGAR Tables (Phase 2)
-- ============================================================================
-- Description: Creates tables for storing SEC (U.S. Securities and Exchange Commission) data
--
-- Tables Created:
--   1. sec_companies - Company master data (CIK, ticker, name, etc.)
--   2. sec_filings - SEC filings (10-K, 10-Q, 8-K, etc.)
--   3. sec_financial_facts - XBRL financial data (Revenue, Assets, etc.)
--   4. sec_institutional_holdings - 13F institutional holdings
--
-- Data Source: SEC EDGAR API (https://www.sec.gov/edgar)
-- API Key Required: No (free public API)
-- Rate Limit: 10 requests per second
--
-- Author: AI Assistant
-- Created: 2025-11-22
-- Version: 2.0
-- ============================================================================

-- Prerequisites: Ensure Phase 1 migration (001_add_phase1_tables.sql) is applied first

BEGIN;

-- ============================================================================
-- Table 1: SEC Companies
-- ============================================================================
-- Stores basic company information from SEC EDGAR database
-- CIK (Central Index Key) is SEC's unique 10-digit identifier for companies

CREATE TABLE IF NOT EXISTS sec_companies (
    id SERIAL PRIMARY KEY,

    -- SEC Identifiers
    cik VARCHAR(10) NOT NULL UNIQUE,  -- 10-digit CIK (e.g., '0000320193' for Apple)
    ticker VARCHAR(10),                -- Stock ticker (can be null if delisted)
    company_name VARCHAR(500) NOT NULL,

    -- Company Details
    sic VARCHAR(10),                   -- Standard Industrial Classification
    sic_description VARCHAR(200),
    category VARCHAR(100),
    entity_type VARCHAR(100),

    -- Address Information (stored as JSON)
    business_address JSONB,            -- {street1, street2, city, state, zip, country}
    mailing_address JSONB,

    -- Contact Information
    phone VARCHAR(50),
    website VARCHAR(500),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    former_names JSONB,                -- Array of previous company names

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for sec_companies
CREATE INDEX idx_sec_company_cik ON sec_companies(cik);
CREATE INDEX idx_sec_company_ticker ON sec_companies(ticker);
CREATE INDEX idx_sec_company_name ON sec_companies(company_name);
CREATE INDEX idx_sec_company_sic ON sec_companies(sic);

-- Comments for sec_companies
COMMENT ON TABLE sec_companies IS 'SEC company master data - stores basic company information from SEC EDGAR';
COMMENT ON COLUMN sec_companies.cik IS 'Central Index Key - SEC''s unique 10-digit identifier';
COMMENT ON COLUMN sec_companies.ticker IS 'Stock ticker symbol (may be null for delisted companies)';
COMMENT ON COLUMN sec_companies.sic IS 'Standard Industrial Classification code';
COMMENT ON COLUMN sec_companies.business_address IS 'Company business address (JSON format)';
COMMENT ON COLUMN sec_companies.former_names IS 'Array of previous company names (JSON format)';

-- ============================================================================
-- Table 2: SEC Filings
-- ============================================================================
-- Stores information about SEC filings (10-K, 10-Q, 8-K, etc.)
--
-- Common Form Types:
--   10-K: Annual report
--   10-Q: Quarterly report
--   8-K: Current report (material events)
--   DEF 14A: Proxy statement
--   13F-HR: Institutional investment manager holdings
--   4: Statement of changes in beneficial ownership

CREATE TABLE IF NOT EXISTS sec_filings (
    id SERIAL PRIMARY KEY,

    -- Foreign Key
    company_id INTEGER NOT NULL REFERENCES sec_companies(id) ON DELETE CASCADE,

    -- Filing Identifiers
    cik VARCHAR(10) NOT NULL,
    accession_number VARCHAR(25) NOT NULL UNIQUE,  -- Unique filing identifier

    -- Filing Details
    form_type VARCHAR(20) NOT NULL,                -- 10-K, 10-Q, 8-K, etc.
    filing_date DATE NOT NULL,
    report_date DATE,                              -- Period end date (for periodic reports)
    accepted_date TIMESTAMP,

    -- Document Information
    primary_document VARCHAR(255),                 -- Main document filename
    primary_doc_description VARCHAR(500),
    document_url VARCHAR(1000),                    -- Full URL to document

    -- Filing Size
    size INTEGER,                                  -- File size in bytes
    file_count INTEGER,                            -- Number of files in submission

    -- Amendment Information
    is_amendment BOOLEAN DEFAULT FALSE,
    is_xbrl BOOLEAN DEFAULT FALSE,                 -- Has XBRL data

    -- Metadata
    items JSONB,                                   -- List of item numbers (for 8-K, etc.)
    raw_data JSONB,                                -- Full raw data from API

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for sec_filings
CREATE INDEX idx_sec_filing_company_id ON sec_filings(company_id);
CREATE INDEX idx_sec_filing_cik ON sec_filings(cik);
CREATE INDEX idx_sec_filing_accession ON sec_filings(accession_number);
CREATE INDEX idx_sec_filing_form_type ON sec_filings(form_type);
CREATE INDEX idx_sec_filing_date ON sec_filings(filing_date);
CREATE INDEX idx_sec_filing_company_form_date ON sec_filings(company_id, form_type, filing_date);
CREATE INDEX idx_sec_filing_cik_date ON sec_filings(cik, filing_date);
CREATE INDEX idx_sec_filing_form_date ON sec_filings(form_type, filing_date);

-- Comments for sec_filings
COMMENT ON TABLE sec_filings IS 'SEC filings - stores information about all types of SEC filings';
COMMENT ON COLUMN sec_filings.accession_number IS 'Unique filing identifier (format: 0000320193-23-000077)';
COMMENT ON COLUMN sec_filings.form_type IS 'Filing form type (10-K, 10-Q, 8-K, etc.)';
COMMENT ON COLUMN sec_filings.filing_date IS 'Date filing was submitted to SEC';
COMMENT ON COLUMN sec_filings.report_date IS 'Period end date for periodic reports';
COMMENT ON COLUMN sec_filings.is_xbrl IS 'Indicates if filing contains XBRL financial data';

-- ============================================================================
-- Table 3: SEC Financial Facts
-- ============================================================================
-- Stores structured financial data extracted from XBRL-formatted filings
--
-- Common US-GAAP Concepts:
--   Revenue / Revenues
--   Assets / AssetsCurrent
--   Liabilities / LiabilitiesCurrent
--   NetIncomeLoss
--   EarningsPerShareBasic / EarningsPerShareDiluted
--   StockholdersEquity
--   CashAndCashEquivalentsAtCarryingValue

CREATE TABLE IF NOT EXISTS sec_financial_facts (
    id SERIAL PRIMARY KEY,

    -- Foreign Key
    company_id INTEGER NOT NULL REFERENCES sec_companies(id) ON DELETE CASCADE,

    -- Identifiers
    cik VARCHAR(10) NOT NULL,

    -- XBRL Taxonomy
    taxonomy VARCHAR(50) NOT NULL,                 -- 'us-gaap', 'dei', 'srt', etc.
    concept VARCHAR(200) NOT NULL,                 -- 'Revenue', 'Assets', etc.
    label VARCHAR(500),                            -- Human-readable label

    -- Time Period
    end_date DATE NOT NULL,                        -- Period end date
    start_date DATE,                               -- Period start date (for duration metrics)
    fiscal_year INTEGER,
    fiscal_period VARCHAR(10),                     -- 'FY', 'Q1', 'Q2', 'Q3', 'Q4'

    -- Value
    value NUMERIC(20, 4),                          -- Numeric value
    unit VARCHAR(20),                              -- 'USD', 'shares', etc.
    decimals INTEGER,                              -- Decimal precision

    -- Form Reference
    form_type VARCHAR(20),                         -- Source form (10-K, 10-Q, etc.)
    filing_date DATE,
    accession_number VARCHAR(25),

    -- Frame Information
    frame VARCHAR(50),                             -- 'CY2023Q4', 'CY2023', etc.

    -- Metadata
    raw_data JSONB,                                -- Full raw fact data

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for sec_financial_facts
CREATE INDEX idx_sec_fact_company_id ON sec_financial_facts(company_id);
CREATE INDEX idx_sec_fact_cik ON sec_financial_facts(cik);
CREATE INDEX idx_sec_fact_concept ON sec_financial_facts(concept);
CREATE INDEX idx_sec_fact_end_date ON sec_financial_facts(end_date);
CREATE INDEX idx_sec_fact_fiscal_year ON sec_financial_facts(cik, fiscal_year);
CREATE INDEX idx_sec_fact_company_concept_date ON sec_financial_facts(company_id, concept, end_date);
CREATE INDEX idx_sec_fact_cik_concept ON sec_financial_facts(cik, concept);
CREATE INDEX idx_sec_fact_concept_date ON sec_financial_facts(concept, end_date);

-- Comments for sec_financial_facts
COMMENT ON TABLE sec_financial_facts IS 'XBRL financial facts - structured financial data from SEC filings';
COMMENT ON COLUMN sec_financial_facts.taxonomy IS 'XBRL taxonomy namespace (us-gaap for US GAAP concepts)';
COMMENT ON COLUMN sec_financial_facts.concept IS 'Financial concept name (Revenue, Assets, etc.)';
COMMENT ON COLUMN sec_financial_facts.end_date IS 'Period end date for the financial fact';
COMMENT ON COLUMN sec_financial_facts.value IS 'Numeric value of the financial fact';
COMMENT ON COLUMN sec_financial_facts.unit IS 'Unit of measurement (USD, shares, etc.)';
COMMENT ON COLUMN sec_financial_facts.frame IS 'Calendar period frame (CY2023Q4 = Calendar Year 2023 Quarter 4)';

-- ============================================================================
-- Table 4: SEC Institutional Holdings
-- ============================================================================
-- Stores institutional investment manager holdings from 13F-HR filings
--
-- 13F filings show what stocks institutional investors (assets > $100M) are holding
-- at the end of each quarter. Famous investors include Warren Buffett, Ray Dalio, etc.

CREATE TABLE IF NOT EXISTS sec_institutional_holdings (
    id SERIAL PRIMARY KEY,

    -- Filing Information
    filer_cik VARCHAR(10) NOT NULL,                -- Institution's CIK
    filer_name VARCHAR(500) NOT NULL,              -- Institution name
    accession_number VARCHAR(25) NOT NULL,         -- 13F filing accession number

    -- Period
    report_date DATE NOT NULL,                     -- Quarter end date
    filing_date DATE,

    -- Holding Information
    holding_company_name VARCHAR(500) NOT NULL,    -- Company being held
    holding_ticker VARCHAR(10),
    holding_cusip VARCHAR(9),                      -- CUSIP identifier (9-character)

    -- Position Details
    shares NUMERIC(20, 4),                         -- Number of shares held
    value NUMERIC(20, 2),                          -- Position value in USD
    share_price NUMERIC(10, 4),                    -- Implied price per share

    -- Position Type
    share_type VARCHAR(20),                        -- 'SH-SOLE', 'SH-SHARED', 'SH-NONE'
    put_call VARCHAR(10),                          -- 'Put', 'Call', or null

    -- Change Information
    shares_change NUMERIC(20, 4),                  -- Change from previous quarter
    shares_change_pct NUMERIC(10, 4),              -- Percentage change

    -- Portfolio Information
    portfolio_weight NUMERIC(10, 6),               -- % of total portfolio

    -- Metadata
    raw_data JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for sec_institutional_holdings
CREATE INDEX idx_sec_holding_filer_cik ON sec_institutional_holdings(filer_cik);
CREATE INDEX idx_sec_holding_ticker ON sec_institutional_holdings(holding_ticker);
CREATE INDEX idx_sec_holding_cusip ON sec_institutional_holdings(holding_cusip);
CREATE INDEX idx_sec_holding_report_date ON sec_institutional_holdings(report_date);
CREATE INDEX idx_sec_holding_filer_date ON sec_institutional_holdings(filer_cik, report_date);
CREATE INDEX idx_sec_holding_ticker_date ON sec_institutional_holdings(holding_ticker, report_date);
CREATE INDEX idx_sec_holding_filer_ticker ON sec_institutional_holdings(filer_cik, holding_ticker);

-- Comments for sec_institutional_holdings
COMMENT ON TABLE sec_institutional_holdings IS '13F institutional holdings - what big investors own';
COMMENT ON COLUMN sec_institutional_holdings.filer_cik IS 'CIK of the institutional investor filing the 13F';
COMMENT ON COLUMN sec_institutional_holdings.filer_name IS 'Name of the institutional investor (e.g., Berkshire Hathaway)';
COMMENT ON COLUMN sec_institutional_holdings.holding_cusip IS 'CUSIP identifier for the security held';
COMMENT ON COLUMN sec_institutional_holdings.shares IS 'Number of shares held';
COMMENT ON COLUMN sec_institutional_holdings.value IS 'Total value of position in USD';
COMMENT ON COLUMN sec_institutional_holdings.report_date IS 'Quarter end date (13F filed within 45 days)';

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Sample Query 1: Get Apple's latest 10-K filing
-- SELECT
--     c.company_name,
--     c.ticker,
--     f.form_type,
--     f.filing_date,
--     f.document_url
-- FROM sec_filings f
-- JOIN sec_companies c ON f.company_id = c.id
-- WHERE c.ticker = 'AAPL' AND f.form_type = '10-K'
-- ORDER BY f.filing_date DESC
-- LIMIT 1;

-- Sample Query 2: Get Apple's revenue history
-- SELECT
--     ff.end_date,
--     ff.value,
--     ff.fiscal_year,
--     ff.fiscal_period
-- FROM sec_financial_facts ff
-- JOIN sec_companies c ON ff.company_id = c.id
-- WHERE c.ticker = 'AAPL'
--   AND ff.concept IN ('Revenue', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax')
--   AND ff.fiscal_period = 'FY'
-- ORDER BY ff.end_date DESC
-- LIMIT 10;

-- Sample Query 3: Get institutional holders of Apple
-- SELECT
--     ih.filer_name,
--     ih.shares,
--     ih.value,
--     ih.portfolio_weight,
--     ih.report_date
-- FROM sec_institutional_holdings ih
-- WHERE ih.holding_ticker = 'AAPL'
--   AND ih.report_date = (SELECT MAX(report_date) FROM sec_institutional_holdings WHERE holding_ticker = 'AAPL')
-- ORDER BY ih.value DESC
-- LIMIT 20;

-- Sample Query 4: Track Berkshire Hathaway's portfolio
-- SELECT
--     ih.holding_ticker,
--     ih.holding_company_name,
--     ih.shares,
--     ih.value,
--     ih.portfolio_weight
-- FROM sec_institutional_holdings ih
-- WHERE ih.filer_name LIKE '%BERKSHIRE HATHAWAY%'
--   AND ih.report_date = (SELECT MAX(report_date) FROM sec_institutional_holdings WHERE filer_name LIKE '%BERKSHIRE HATHAWAY%')
-- ORDER BY ih.value DESC
-- LIMIT 20;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify tables were created
SELECT
    table_name,
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('sec_companies', 'sec_filings', 'sec_financial_facts', 'sec_institutional_holdings')
ORDER BY table_name;

-- Verify indexes were created
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('sec_companies', 'sec_filings', 'sec_financial_facts', 'sec_institutional_holdings')
ORDER BY tablename, indexname;

COMMIT;

-- ============================================================================
-- Migration Complete
-- ============================================================================
--
-- Tables Created: 4
--   ✓ sec_companies (12 columns, 4 indexes)
--   ✓ sec_filings (18 columns, 8 indexes)
--   ✓ sec_financial_facts (19 columns, 8 indexes)
--   ✓ sec_institutional_holdings (20 columns, 7 indexes)
--
-- Total Indexes: 27
--
-- Next Steps:
--   1. Run test script: python scripts/test_sec_edgar.py
--   2. Start collecting data using SEC EDGAR collector
--   3. Build analysis features for SEC data
--   4. Create dashboard for visualization
--
-- ============================================================================
