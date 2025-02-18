# Excel Data Processor with AI Assistance

A powerful Streamlit-based application for processing Excel files with AI-powered suggestions for data analysis. This tool allows users to upload Excel files, create derived columns, and define flag rules with the assistance of AI suggestions.

##System Design Doc:
(https://docs.google.com/document/d/1GPcOYBDlOM6ZyYZLHkt7jJ1CWcIAbjOxqd4Qt-6rPy4/edit?usp=sharing)[https://docs.google.com/document/d/1GPcOYBDlOM6ZyYZLHkt7jJ1CWcIAbjOxqd4Qt-6rPy4/edit?usp=sharing]

## 🌟 Features

### 1. Excel File Management
- Upload Excel files (.xlsx, .xls)
- Preview data with interactive row selection
- Crop data to selected rows
- Export processed data to CSV

### 2. Derived Columns
- Create new columns using pandas-compatible formulas
- AI-suggested column operations
- Track column creation history
- Remove columns with one click
- Real-time formula evaluation

### 3. Flag Rules
- Define custom flag rules using simple conditions
- AI-suggested flagging rules
- Track rule history
- Remove rules easily
- Automatic flag column creation

### 4. AI Integration
- Powered by Google's Gemini AI
- Context-aware suggestions
- Natural language query processing
- Interactive suggestion application
- Example operations for reference

## 🛠️ Technical Architecture

### Project Structure
```
excel_processor/
├── README.md
├── requirements.txt
├── .env.example
├── setup.py
└── src/
    ├── __init__.py
    ├── main.py
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py
    ├── services/
    │   ├── __init__.py
    │   ├── ai_service.py
    │   ├── excel_processor.py
    │   └── logger.py
    └── ui/
        ├── __init__.py
        ├── components.py
        └── pages.py
```

### Key Components

1. **ExcelProcessor (services/excel_processor.py)**
   - Core data processing functionality
   - DataFrame management
   - Column and rule history tracking
   - Error handling and validation

2. **AIService (services/ai_service.py)**
   - AI integration using LiteLLM
   - Prompt engineering
   - Response processing
   - Suggestion generation

3. **UI Components (ui/)**
   - Streamlit interface components
   - User interaction handling
   - Data visualization
   - State management

## 🚀 Getting Started

### Prerequisites
- Python 3.12.9
- Virtual environment (recommended)
- Google API Key for AI features

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/excel-processor.git
cd excel-processor
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running the Application
```bash
streamlit run src/main.py
```

## 💡 Usage Guide

### 1. Upload Data
- Click "Upload Excel File" button
- Select your Excel file
- Preview data and adjust row selection if needed

### 2. Create Derived Columns
```python
# Example formulas:
Revenue = Price * Quantity
Discount = Price * 0.1
Profit_Margin = (Price - Cost) / Price
```

### 3. Define Flag Rules
```python
# Example rules:
Price > 100
Quantity < 5
Revenue > 1000
```

### 4. Use AI Assistance
1. Enter your query in natural language
2. Review AI suggestions
3. Apply suggested operations with one click

## 🔧 Configuration

### Environment Variables
```env
GOOGLE_API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

### Customization Options
- Modify logging configuration in `services/logger.py`
- Adjust AI prompts in `services/ai_service.py`
- Customize UI components in `ui/components.py`

- Include docstrings for all functions/classes
- Add comments for complex logic


