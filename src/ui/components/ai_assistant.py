import streamlit as st
from src.services.ai_service import AIService
from src.utils.logger import AppLogger

class AIAssistantComponent:
    def __init__(self):
        self.ai_service = AIService()
        self.logger = AppLogger()
    
    def render(self, columns: list):
        st.header("AI Assistant")
        
        user_query = st.text_area(
            "Describe what columns or flags you want to create:",
            placeholder="e.g., 'I want a new column showing twice the price and flag items with quantity less than 20'"
        )
        
        if st.button("Get AI Suggestions"):
            if user_query:
                suggestions = self.ai_service.get_suggestions(user_query, columns)
                st.session_state.suggestions = suggestions
                self._render_suggestions(suggestions)
    
    def _render_suggestions(self, suggestions: dict):
        if suggestions.get("derived_columns"):
            self._render_derived_columns(suggestions["derived_columns"])
        
        if suggestions.get("flag_rules"):
            self._render_flag_rules(suggestions["flag_rules"]) 