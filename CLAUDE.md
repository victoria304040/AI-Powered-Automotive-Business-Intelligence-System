# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Setup

### Python Environment
- **Virtual Environment**: The project uses `new_venv` located in `PycharmProjects/DAD/new_venv/`
- **Python Version**: Python 3.13
- **Package Management**: Uses pip with requirements managed in virtual environment

### Key Dependencies
- **AI/ML Libraries**: OpenAI API, LangChain, LangChain OpenAI, LangChain Experimental
- **Data Processing**: pandas, numpy
- **Web Interface**: Streamlit for interactive dashboard
- **File Processing**: openpyxl for Excel file handling

## Project Architecture

This is the HOTAI MOTOR sales data analysis system - an automotive sales dashboard and AI assistant that processes MBIS (Motor Business Intelligence System) sales data and target comparisons.

### Core Files Structure
```
HOTAI MOTOR/
├── app.py                    # Streamlit web interface
├── solution_combine.py       # Main LangChain agent orchestrator
├── solution1.py             # General data exploration tools
├── solution3.py             # Target vs actual comparison tools
├── Mapping Dataframe.xlsx   # Dealer code mapping table
├── secret_key              # OpenAI API key storage
├── MBIS實績_*.xlsx         # Sales performance data files
├── 經銷商目標_*.xlsx        # Sales target data files
└── 先沒有要用的/            # Archive directory for test data
```

### Application Architecture

#### Core Components
1. **Streamlit Dashboard** (`app.py`): Web interface for user interaction
2. **LangChain Agent** (`solution_combine.py`): AI agent orchestrator with dual analysis modes
3. **Data Analysis Tools** (`solution1.py`, `solution3.py`): Specialized toolsets for different analysis types

#### Data Processing Pipeline
1. **Data Input**: Excel files with structured sales data (targets and actuals)
2. **Classification**: Automatic file type detection (target vs actual data)
3. **Analysis**: Dual-mode processing based on query type
4. **Output**: Structured responses with markdown tables and summaries

## Common Development Commands

### Running the Application
```bash
# Navigate to project directory
cd "C:\Users\yijialee\PycharmProjects\DAD\HOTAI MOTOR"

# Activate virtual environment
..\new_venv\Scripts\activate

# Run Streamlit dashboard
streamlit run app.py

# Run individual analysis modules (for testing)
python solution_combine.py
python solution1.py
python solution3.py
```

### Testing Commands
```bash
# Test individual components
python test.py
python combine_test.py

# Data processing utilities
python 格式轉換.py
python 資料匯入.py
python output.py
```

## Data Architecture and Processing

### Excel Data Structure

#### Target Data Files (`經銷商目標_*.xlsx`)
- **Naming Pattern**: `經銷商目標_YYYY上半年.xlsx` or `經銷商目標_YYYY下半年.xlsx`
- **Key Columns**:
  - `目標種類`: Target type (`1`=受訂/orders, `2`=販賣/sales)
  - `X月目標`, `Y月目標`: Monthly targets or generic `目標數`
  - Dealer and location identifiers

#### Actual Data Files (`MBIS實績_*.xlsx`)
- **Naming Pattern**: `MBIS實績_YYYY上半年.xlsx` or monthly files
- **Key Columns**:
  - `實績種類`: Performance type (`27`=受訂/orders, `3D`=販賣/sales)
  - `受訂數`: Order quantity (for orders)
  - `銷售數`: Sales quantity (for sales)
  - `台數`: Generic quantity field (unified reference)

#### Mapping Table (`Mapping Dataframe.xlsx`)
- Dealer code to dealer name mappings
- Location code to location name mappings
- Used for translating codes to human-readable names

### Data Processing Patterns

#### Dual Analysis Modes
1. **General Data Exploration**: Rankings, time-series analysis, statistical summaries
2. **Target vs Actual Comparison**: Performance analysis, achievement rates, variance analysis

#### Column Type Handling
```python
# Date columns - force datetime conversion
df['日期'] = pd.to_datetime(df['日期'], errors='coerce')

# String columns - clean and normalize
df['實績種類'] = df['實績種類'].astype(str).str.strip()

# Always use string comparison for coded fields
filtered = df[df['實績種類'] == '27']  # Correct: string '27'
```

#### Aggregation Rules
- **Mandatory GroupBy**: All statistical analysis must group by relevant dimensions
- **Preserve Original Values**: Keep all raw values including -1, 0 for accurate analysis
- **Multi-level Ranking**: First group by category, then by sub-category

## LangChain Agent Configuration

### Agent Tools
- `list_files()`: Directory file enumeration
- `read_excel_head()`: File preview and structure analysis  
- `read_excel_file()`: Full file loading
- `analyze_dataframe()`: General data analysis
- `list_and_classify_files()`: Automatic file type classification
- `load_excel_file()`: Multi-sheet file loading
- `compare_target_vs_actual()`: Performance comparison analysis

### Model Configuration
- **Model**: GPT-4 (configurable in solution files)
- **Temperature**: 0 (deterministic responses)
- **Agent Type**: OpenAI Functions Agent
- **Verbose Mode**: Enabled for debugging

### Business Logic Rules
- **Achievement Rate**: 實績台數 / 目標台數 × 100%
- **Growth Rate**: 今年實績台數 / 去年實績台數 × 100%
- **Progress Rate**: Used for in-month tracking vs targets
- **Common Abbreviations**: CC (C CROSS), YC (Y CROSS), HV/HEV (hybrid vehicles)

## Configuration Management

### API Keys and Secrets
- OpenAI API key stored in `secret_key` file (not committed to git)
- Environment variable setup at runtime in each module
- Key loaded automatically by application scripts

### Data File Conventions
- Excel files use consistent Japanese/Chinese field naming
- Date formats standardized with `pd.to_datetime()` conversion
- Numeric fields handle missing values and negative numbers appropriately
- File naming follows `類型_時期.xlsx` pattern

## Important Architecture Notes

- **Chinese Language Support**: All modules designed for Traditional Chinese text processing
- **Multi-Agent Architecture**: LangChain orchestrates multiple specialized analysis agents
- **Memory Management**: Global dataframes dictionary maintains loaded data across tool calls
- **Error Handling**: Comprehensive error handling for file loading and API calls
- **Performance Optimization**: Efficient pandas operations with proper indexing and grouping

## Module-Specific Guidance

### When working with app.py:
- Streamlit session state manages conversation history
- Query routing happens through `solution_combine.py`
- UI supports markdown rendering for structured responses

### When working with solution_combine.py:
- Acts as the main orchestrator for all analysis requests
- Automatically detects analysis type and routes to appropriate tools
- Maintains business logic definitions and calculation rules
- Uses mapping table for dealer/location name resolution

### When working with data analysis:
- Always check and convert date columns to datetime
- Use string comparisons for coded categorical fields
- Group by both codes and names for comprehensive analysis
- Preserve original data values in aggregations
- Follow the established calculation definitions for business metrics