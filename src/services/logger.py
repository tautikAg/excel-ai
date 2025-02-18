"""
Logging service for the application.
"""
import logging
import streamlit as st

class AppLogger:
    """Application logger with Streamlit integration"""
    
    def __init__(self):
        """Initialize logger with basic configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('ExcelProcessor')

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
        
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
        st.error(message)
        
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message) 