import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional, List
import re
from litellm import completion
from pydantic import BaseModel, ConfigDict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DerivedColumn(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    formula: str
    description: str

class FlagRule(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    rule: str
    description: str

class AnalysisSuggestions(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    derived_columns: List[DerivedColumn]
    flag_rules: List[FlagRule]

class AIHelper:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
    def get_suggestions(self, query: str, columns: list) -> dict:
        """Get AI suggestions for derived columns and flag rules"""
        try:
            prompt = f"""Given these columns: {', '.join(columns)}
            And user query: "{query}"
            You are a data analysis expert. Based on the user's query, suggest derived columns and flag rules.
            Provide suggestions in this exact JSON format:
            {{
                "derived_columns": [
                    {{"name": "example_name", "formula": "example_formula", "description": "what this does"}}
                ],
                "flag_rules": [
                    {{"rule": "example_rule", "description": "what this flags"}}
                ]
            }}
            Use valid pandas operations and ensure the JSON is properly formatted."""
            
            st.write("Sending prompt to LLM:", prompt)
            
            response = completion(
                model="gemini/gemini-1.5-pro",
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,
                response_format={"type": "json_object"}  # Specify JSON response format
            )
            
            st.write("Raw response from LLM:", response)
            
            # Get the content from response
            content = response.choices[0].message.content
            st.write("Content from response:", content)
            
            # Parse JSON if it's a string
            if isinstance(content, str):
                try:
                    import json
                    suggestions = json.loads(content)
                    st.write("Parsed JSON:", suggestions)
                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse JSON: {str(e)}")
                    return {"derived_columns": [], "flag_rules": []}
            else:
                suggestions = content
            
            # Validate against our Pydantic model
            try:
                validated_suggestions = AnalysisSuggestions.model_validate(suggestions)
                st.write("Validated suggestions:", validated_suggestions)
                return validated_suggestions.model_dump()
            except Exception as e:
                st.error(f"Failed to validate suggestions: {str(e)}")
                return {"derived_columns": [], "flag_rules": []}
            
        except Exception as e:
            st.error(f"Error getting AI suggestions: {str(e)}")
            st.error(f"Error type: {type(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return {"derived_columns": [], "flag_rules": []}

class ExcelProcessor:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.column_history = []
        self.rule_history = []
        self.selected_rows = None
        self.suggestions = None
    
    def load_excel(self, file):
        """Load Excel file into DataFrame"""
        try:
            self.df = pd.read_excel(file)
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False
    
    def crop_selection(self, start_row, end_row):
        """Crop DataFrame to selected rows"""
        if self.df is not None:
            self.df = self.df.iloc[start_row:end_row+1].copy()
            return True
        return False
    
    def add_derived_column(self, column_name: str, formula: str) -> bool:
        """Add a new derived column based on formula"""
        try:
            # Clean the formula
            formula = formula.strip()
            
            # Evaluate the formula
            self.df[column_name] = self.df.eval(formula)
            
            # Store in history
            self.column_history.append({
                "name": column_name,
                "formula": formula
            })
            return True
        except Exception as e:
            st.error(f"Error creating derived column: {str(e)}")
            return False
    
    def add_flag_rule(self, rule: str) -> bool:
        """Add a new flag based on rule condition"""
        try:
            # Clean the rule
            rule = rule.strip()
            
            # Create flag column name
            flag_name = f"Flag_{rule}"
            
            # Evaluate the rule
            self.df[flag_name] = self.df.eval(rule)
            
            # Store in history
            self.rule_history.append(rule)
            return True
        except Exception as e:
            st.error(f"Error applying flag rule: {str(e)}")
            return False
    
    def get_column_names(self) -> list:
        """Get list of current column names"""
        return list(self.df.columns) if self.df is not None else []

    def suggest_operations(self, query: str) -> dict:
        """Get AI suggestions for operations"""
        if not hasattr(self, 'ai_helper'):
            self.ai_helper = AIHelper()
        
        columns = self.get_column_names()
        self.suggestions = self.ai_helper.get_suggestions(query, columns)
        return self.suggestions

def main():
    st.set_page_config(
        page_title="Excel Data Processor",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Excel Data Processor")
    
    # Initialize processor
    if 'processor' not in st.session_state:
        st.session_state.processor = ExcelProcessor()
    
    # File upload section
    st.header("1. Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file:
        if st.session_state.processor.load_excel(uploaded_file):
            st.success("File loaded successfully!")
            
            # Data Preview with Row Selection
            st.subheader("Data Preview")
            st.write("Select rows by dragging the slider:")
            
            # Row selection slider
            row_count = len(st.session_state.processor.df)
            start_row, end_row = st.select_slider(
                "Select row range",
                options=range(row_count),
                value=(0, row_count-1),
                key="row_range"
            )
            
            # Display selected data
            preview_df = st.session_state.processor.df.iloc[start_row:end_row+1]
            st.dataframe(preview_df)
            
            # Crop button
            if st.button("Crop to Selection"):
                if st.session_state.processor.crop_selection(start_row, end_row):
                    st.success("Data cropped successfully!")
            
            # AI Assistant Section
            st.header("AI Assistant")
            user_query = st.text_area("Describe what columns or flags you want to create:", 
                placeholder="e.g., 'I want a new column showing twice the price and flag items with quantity less than 20'")
            
            if st.button("Get AI Suggestions"):
                if user_query:
                    suggestions = st.session_state.processor.suggest_operations(user_query)
                    # Store suggestions in session state
                    st.session_state.suggestions = suggestions
            
            # Show suggestions if they exist in session state
            if hasattr(st.session_state, 'suggestions') and st.session_state.suggestions:
                suggestions = st.session_state.suggestions
                
                # Show Derived Column Suggestions
                if suggestions.get("derived_columns"):
                    st.subheader("Suggested Derived Columns")
                    for idx, col in enumerate(suggestions["derived_columns"]):
                        with st.expander(f"{col['name']}: {col['description']}"):
                            st.write(f"Formula: `{col['formula']}`")
                            if st.button("Apply This Column", key=f"col_{idx}"):
                                if st.session_state.processor.add_derived_column(col['name'], col['formula']):
                                    st.success(f"Added column: {col['name']}")
                
                # Show Flag Rule Suggestions
                if suggestions.get("flag_rules"):
                    st.subheader("Suggested Flag Rules")
                    for idx, flag in enumerate(suggestions["flag_rules"]):
                        with st.expander(f"Flag: {flag['description']}"):
                            st.write(f"Rule: `{flag['rule']}`")
                            if st.button("Apply This Rule", key=f"flag_{idx}"):
                                if st.session_state.processor.add_flag_rule(flag['rule']):
                                    st.success(f"Added flag rule: {flag['rule']}")
                                    # Use st.rerun() instead of experimental_rerun
                                    st.rerun()
            
            # Derived Columns Section
            st.header("2. Create Derived Columns")
            
            # Available columns display
            st.info("Available columns: " + ", ".join(st.session_state.processor.get_column_names()))
            
            # Formula input
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                new_col_name = st.text_input("Column Name", key="new_col_name")
            with col2:
                formula = st.text_input("Formula (e.g., Price * Quantity)", key="formula")
            with col3:
                if st.button("Add Column"):
                    if new_col_name and formula:
                        if st.session_state.processor.add_derived_column(new_col_name, formula):
                            st.success(f"Added column: {new_col_name}")
            
            # Display column history
            if st.session_state.processor.column_history:
                st.subheader("Created Columns")
                for col in st.session_state.processor.column_history:
                    st.code(f"{col['name']} = {col['formula']}")
            
            # Flagging Rules Section
            st.header("3. Define Flag Rules")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                rule = st.text_input("Rule (e.g., Price > 100)", key="rule")
            with col2:
                if st.button("Add Rule"):
                    if rule:
                        if st.session_state.processor.add_flag_rule(rule):
                            st.success(f"Added flag for rule: {rule}")
            
            # Display rule history
            if st.session_state.processor.rule_history:
                st.subheader("Applied Rules")
                for rule in st.session_state.processor.rule_history:
                    st.code(rule)
            
            # Final Results
            if st.session_state.processor.df is not None:
                st.header("4. Processed Data")
                st.dataframe(st.session_state.processor.df)
                
                # Export button
                if st.download_button(
                    label="Download Processed Data",
                    data=st.session_state.processor.df.to_csv(index=False).encode('utf-8'),
                    file_name="processed_data.csv",
                    mime="text/csv"
                ):
                    st.success("Data downloaded successfully!")

if __name__ == "__main__":
    main() 