import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional, List
import re
from litellm import completion
from pydantic import BaseModel, ConfigDict
import os
from dotenv import load_dotenv
from utils.logger import AppLogger
import json

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
                model="gemini/gemini-2.0-flash",
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,
                cache_control={"type": "ephemeral"},
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
        self.logger = AppLogger()
        self.current_file = None
    
    def load_excel(self, file):
        """Load Excel file into DataFrame"""
        try:
            # Only load if DataFrame is None or file has changed
            if self.df is None or hasattr(self, 'current_file') and self.current_file != file.name:
                self.df = pd.read_excel(file)
                self.current_file = file.name
                self.logger.info(f"Loaded new file: {file.name}")
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
            self.logger.info(f"Starting to add flag rule: {rule}")
            
            if self.df is None:
                self.logger.error("DataFrame is None")
                return False
                
            # Clean the rule and ensure it's a valid pandas expression
            rule = rule.strip()
            
            # Create flag column name
            flag_name = f"Flag_{rule}"
            
            # Create a copy of DataFrame to avoid modifying original
            df_copy = self.df.copy()
            
            try:
                # First evaluate the condition
                result = df_copy.eval(rule)
                self.logger.debug(f"Rule evaluation result: {result.head().tolist()}")
                
                # Add the flag column
                df_copy[flag_name] = result
                
                # Update the main DataFrame
                self.df = df_copy
                
                # Store in history
                self.rule_history.append(rule)
                
                # Update session state with the new DataFrame
                if 'processor' in st.session_state:
                    st.session_state.processor.df = self.df
                    st.session_state.processor.rule_history = self.rule_history
                
                self.logger.info(f"Flag rule applied. Current columns: {self.df.columns.tolist()}")
                return True
                
            except Exception as e:
                self.logger.error(f"Rule evaluation failed: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in add_flag_rule: {str(e)}")
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

    def remove_derived_column(self, column_name: str) -> bool:
        """Remove a derived column"""
        try:
            if column_name in self.df.columns:
                self.df = self.df.drop(columns=[column_name])
                # Remove from history
                self.column_history = [col for col in self.column_history if col['name'] != column_name]
                return True
            return False
        except Exception as e:
            st.error(f"Error removing column: {str(e)}")
            return False

    def remove_flag_rule(self, rule: str) -> bool:
        """Remove a flag rule and its corresponding column"""
        try:
            flag_col = f"Flag_{rule}"
            if flag_col in self.df.columns:
                self.df = self.df.drop(columns=[flag_col])
            # Remove from history
            self.rule_history = [r for r in self.rule_history if r != rule]
            return True
        except Exception as e:
            st.error(f"Error removing flag rule: {str(e)}")
            return False

def main():
    logger = AppLogger()
    logger.info("Application started")
    
    st.set_page_config(
        page_title="Excel Data Processor",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Excel Data Processor")
    
    # File upload section
    st.header("1. Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file:
        logger.info(f"File uploaded: {uploaded_file.name}")
        
        # Initialize processor if not in session state
        if 'processor' not in st.session_state:
            st.session_state.processor = ExcelProcessor()
            
        if st.session_state.processor.load_excel(uploaded_file):
            logger.info("File loaded successfully")
            
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

            # Add example suggestions in a collapsible section
            with st.expander("See example operations you can request"):
                st.markdown("""
                **Example requests you can try:**
                
                1. "Calculate total revenue by multiplying price and quantity, and flag items with revenue above $1000"
                2. "Create a discount column that's 10% of the price, and flag items where quantity is less than 5"
                3. "Add a profit margin column that's 20% of the price, and flag items where margin is below $10"
                4. "Create a shipping cost column based on weight (weight * 2), and flag heavy items above 50kg"
                5. "Calculate price per unit by dividing total price by quantity, and flag items where unit price > $100"
                """)

            user_query = st.text_area(
                "Describe what columns or flags you want to create:", 
                placeholder="e.g., 'Calculate total revenue by multiplying price and quantity, and flag items with revenue above $1000'"
            )

            # Add a "Try Example" button
            if st.button("Try an Example Query"):
                example_query = "Calculate total revenue by multiplying price and quantity, and flag items with revenue above $1000"
                # Update the text area with the example query
                st.session_state['example_query'] = example_query
                user_query = example_query

            if st.button("Get AI Suggestions"):
                if user_query:
                    with st.spinner("Generating suggestions..."):
                        suggestions = st.session_state.processor.suggest_operations(user_query)
                        # Store suggestions in session state
                        st.session_state.suggestions = suggestions
                else:
                    st.warning("Please enter a query or try an example query first.")
            
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
                                logger.info(f"Attempting to apply flag rule: {flag['rule']}")
                                if st.session_state.processor.add_flag_rule(flag['rule']):
                                    st.success(f"Added flag rule: {flag['rule']}")
                                    
                                    # Show updated data immediately
                                    st.write("Updated DataFrame:")
                                    st.dataframe(st.session_state.processor.df)
                                    
                                    # Force session state update
                                    st.session_state.processor = st.session_state.processor
                                    
                                    # Single rerun to refresh the page
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
                for idx, col in enumerate(st.session_state.processor.column_history):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.code(f"{col['name']} = {col['formula']}")
                    with col2:
                        if st.button("❌", key=f"remove_col_{idx}"):
                            # Remove column from DataFrame
                            if col['name'] in st.session_state.processor.df.columns:
                                st.session_state.processor.df = st.session_state.processor.df.drop(columns=[col['name']])
                            # Remove from history
                            st.session_state.processor.column_history.pop(idx)
                            st.rerun()
            
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
                for idx, rule in enumerate(st.session_state.processor.rule_history):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.code(rule)
                    with col2:
                        if st.button("❌", key=f"remove_rule_{idx}"):
                            # Remove flag column from DataFrame
                            flag_col = f"Flag_{rule}"
                            if flag_col in st.session_state.processor.df.columns:
                                st.session_state.processor.df = st.session_state.processor.df.drop(columns=[flag_col])
                            # Remove from history
                            st.session_state.processor.rule_history.pop(idx)
                            st.rerun()
            
            # Final Results
            if st.session_state.processor.df is not None:
                st.header("4. Processed Data")
                
                # Show column names for debugging
                st.write("Current columns:", st.session_state.processor.df.columns.tolist())
                
                # Display full DataFrame
                st.dataframe(st.session_state.processor.df)
                
                # Export button with all columns
                if st.download_button(
                    label="Download Processed Data",
                    data=st.session_state.processor.df.to_csv(index=False).encode('utf-8'),
                    file_name="processed_data.csv",
                    mime="text/csv"
                ):
                    st.success("Data downloaded successfully!")

if __name__ == "__main__":
    main() 