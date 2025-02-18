from typing import Dict, List
import os
from litellm import completion
from src.core.models import AnalysisSuggestions
from src.utils.logger import AppLogger

class AIService:
    """
    Service for handling AI-related operations using LLM.
    
    This service manages interactions with the LLM API for generating
    data analysis suggestions based on user queries.
    """
    
    def __init__(self):
        """Initialize the AI service with API key and logger."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.logger = AppLogger()
        
    def get_suggestions(self, query: str, columns: List[str]) -> Dict:
        """
        Get AI suggestions for data analysis based on user query.
        
        Args:
            query (str): User's natural language query
            columns (List[str]): Available DataFrame columns
            
        Returns:
            Dict: Suggestions containing derived columns and flag rules
            
        Example:
            >>> service.get_suggestions("flag expensive items", ["Price", "Quantity"])
            {
                "derived_columns": [...],
                "flag_rules": [{"rule": "Price > 100", "description": "..."}]
            }
        """
        try:
            prompt = self._build_prompt(query, columns)
            response = self._get_llm_response(prompt)
            return self._process_response(response)
        except Exception as e:
            self.logger.error(f"AI suggestion error: {str(e)}", exc_info=True)
            return {"derived_columns": [], "flag_rules": []}
    
    def _build_prompt(self, query: str, columns: List[str]) -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            query (str): User's query
            columns (List[str]): Available columns
            
        Returns:
            str: Formatted prompt for LLM
        """
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
        """
        Get response from LLM API.
        
        Args:
            prompt (str): Formatted prompt
            
        Returns:
            Response from LLM API
        """
        return completion(
            model="gemini/gemini-2.0-flash",
            messages=[{"role": "user", "content": prompt}],
            api_key=self.api_key,
            cache_control={"type": "ephemeral"},
            response_format={"type": "json_object"}
        ) 