from typing import Optional, Tuple
import pandas as pd
from src.utils.logger import AppLogger

class ExcelService:
    """
    Service for handling Excel file operations and data transformations.
    
    This service manages Excel file loading and formula evaluations,
    providing error handling and logging.
    """
    
    def __init__(self):
        """Initialize the Excel service with logger."""
        self.logger = AppLogger()
    
    def load_excel(self, file) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Load Excel file into pandas DataFrame.
        
        Args:
            file: File-like object containing Excel data
            
        Returns:
            Tuple[Optional[pd.DataFrame], str]: (DataFrame if successful, error message if any)
            
        Example:
            >>> df, error = service.load_excel(uploaded_file)
            >>> if error:
            >>>     print(f"Error: {error}")
        """
        try:
            df = pd.read_excel(file)
            return df, ""
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def apply_formula(self, df: pd.DataFrame, formula: str) -> Tuple[Optional[pd.Series], str]:
        """
        Apply pandas formula to DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            formula (str): Pandas-compatible formula
            
        Returns:
            Tuple[Optional[pd.Series], str]: (Result series if successful, error message if any)
            
        Example:
            >>> result, error = service.apply_formula(df, "Price * Quantity")
            >>> if error:
            >>>     print(f"Error: {error}")
        """
        try:
            result = df.eval(formula)
            return result, ""
        except Exception as e:
            error_msg = f"Error evaluating formula: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg 