import streamlit as st
from src.ui.components.file_upload import FileUploadComponent
from src.ui.components.data_preview import DataPreviewComponent
from src.ui.components.ai_assistant import AIAssistantComponent
from src.ui.components.data_processor import DataProcessorComponent
from src.utils.logger import AppLogger

def main():
    logger = AppLogger()
    logger.info("Application started")
    
    st.set_page_config(
        page_title="Excel Data Processor",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Excel Data Processor")
    
    # Initialize components
    file_upload = FileUploadComponent()
    data_preview = DataPreviewComponent()
    ai_assistant = AIAssistantComponent()
    data_processor = DataProcessorComponent()
    
    # Render UI
    uploaded_file = file_upload.render()
    
    if uploaded_file:
        data_preview.render(uploaded_file)
        ai_assistant.render(data_preview.get_columns())
        data_processor.render()

if __name__ == "__main__":
    main() 