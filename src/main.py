"""
Main entry point for the Excel Data Processor application.
"""
from dotenv import load_dotenv
from src.ui.pages import main_page

def main():
    """Application entry point"""
    # Load environment variables
    load_dotenv()
    
    # Run the main Streamlit page
    main_page()

if __name__ == "__main__":
    main() 