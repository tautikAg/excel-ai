"""
Data models for the application using Pydantic.
"""
from typing import List
from pydantic import BaseModel, ConfigDict

class DerivedColumn(BaseModel):
    """Schema for derived column data"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    formula: str
    description: str

class FlagRule(BaseModel):
    """Schema for flag rule data"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    rule: str
    description: str

class AnalysisSuggestions(BaseModel):
    """Schema for AI suggestions response"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    derived_columns: List[DerivedColumn]
    flag_rules: List[FlagRule] 