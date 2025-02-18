"""
Service for handling Excel file processing and data operations.
"""
from typing import Optional, List, Dict
import pandas as pd
import streamlit as st
import numpy as np
from src.services.logger import AppLogger
from src.services.ai_service import AIService

class ExcelProcessor:
    """Handles Excel file processing and data operations"""
    
    def __init__(self):
        """Initialize ExcelProcessor with required attributes"""
        self.df: Optional[pd.DataFrame] = None
        self.column_history: List[Dict] = []
        self.rule_history: List[str] = []
        self.logger = AppLogger()
        self.current_file = None
        self.ai_service = AIService()

    def load_excel(self, file) -> bool:
        """Load Excel file into DataFrame"""
        try:
            if self.df is None or self.current_file != file.name:
                self.df = pd.read_excel(file)
                self.current_file = file.name
                self.logger.info(f"Loaded file: {file.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading file: {str(e)}")
            return False

    def get_column_names(self) -> List[str]:
        """Get list of column names"""
        return self.df.columns.tolist() if self.df is not None else []

    def crop_selection(self, start_row: int, end_row: int) -> bool:
        """Crop DataFrame to selected rows"""
        try:
            if self.df is not None:
                self.df = self.df.iloc[start_row:end_row+1].copy()
                self.logger.info(f"Cropped data to rows {start_row}-{end_row}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error cropping data: {str(e)}")
            return False

    def add_derived_column(self, column_name: str, formula: str) -> bool:
        """Add a new derived column based on formula"""
        try:
            formula = formula.strip()
            self.df[column_name] = self.df.eval(formula)
            self.column_history.append({
                "name": column_name,
                "formula": formula
            })
            self.logger.info(f"Added column: {column_name} = {formula}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating column: {str(e)}")
            return False

    def remove_derived_column(self, column_name: str) -> bool:
        """Remove a derived column"""
        try:
            if column_name in self.df.columns:
                self.df = self.df.drop(columns=[column_name])
                self.column_history = [
                    col for col in self.column_history 
                    if col['name'] != column_name
                ]
                self.logger.info(f"Removed column: {column_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing column: {str(e)}")
            return False

    def add_flag_rule(self, rule: str) -> bool:
        """Add a new flag based on rule condition"""
        try:
            rule = rule.strip()
            flag_col = f"Flag_{rule}"
            self.df[flag_col] = self.df.eval(rule)
            self.rule_history.append(rule)
            self.logger.info(f"Added flag rule: {rule}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding flag rule: {str(e)}")
            return False

    def remove_flag_rule(self, rule: str) -> bool:
        """Remove a flag rule and its column"""
        try:
            flag_col = f"Flag_{rule}"
            if flag_col in self.df.columns:
                self.df = self.df.drop(columns=[flag_col])
                self.rule_history.remove(rule)
                self.logger.info(f"Removed flag rule: {rule}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing flag rule: {str(e)}")
            return False

    def suggest_operations(self, query: str) -> Dict:
        """Get AI suggestions for operations"""
        try:
            return self.ai_service.get_suggestions(query, self.get_column_names())
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {str(e)}")
            return {"derived_columns": [], "flag_rules": []} 