"""
Service for handling AI-related operations using LiteLLM.
"""
import os
from typing import Dict, List
import streamlit as st
from litellm import completion
from src.models.schemas import AnalysisSuggestions

class AIService:
    """Handles AI operations and suggestions"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
    def get_suggestions(self, query: str, columns: List[str]) -> Dict:
        """
        Get AI suggestions for derived columns and flag rules
        
        Args:
            query: User's natural language query
            columns: List of available column names
            
        Returns:
            Dict containing suggested derived columns and flag rules
        """
        try:
            prompt = self._build_prompt(query, columns)
            response = self._get_llm_response(prompt)
            return self._process_response(response)
        except Exception as e:
            st.error(f"Error getting AI suggestions: {str(e)}")
            return {"derived_columns": [], "flag_rules": []}
    
    def _build_prompt(self, query: str, columns: List[str]) -> str:
        """Build the prompt for the LLM"""
        return f"""Given these columns: {', '.join(columns)}
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
    
    def _get_llm_response(self, prompt: str):
        """Get response from LLM"""
        return completion(
            model="gemini/gemini-2.0-flash",
            messages=[{"role": "user", "content": prompt}],
            api_key=self.api_key,
            cache_control={"type": "ephemeral"},
            response_format={"type": "json_object"}
        )
    
    def _process_response(self, response) -> Dict:
        """Process and validate LLM response"""
        try:
            content = response.choices[0].message.content
            if isinstance(content, str):
                import json
                suggestions = json.loads(content)
            else:
                suggestions = content
            
            validated_suggestions = AnalysisSuggestions.model_validate(suggestions)
            return validated_suggestions.model_dump()
        except Exception as e:
            st.error(f"Failed to process suggestions: {str(e)}")
            return {"derived_columns": [], "flag_rules": []} 