from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class DerivedColumn(BaseModel):
    """
    Represents a derived column configuration.
    
    Attributes:
        name (str): Name of the new column
        formula (str): Pandas-compatible formula to calculate column values
        description (str): Human-readable description of what the column represents
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    formula: str
    description: str

class FlagRule(BaseModel):
    """
    Represents a flag rule configuration.
    
    Attributes:
        rule (str): Pandas-compatible boolean expression for flagging
        description (str): Human-readable description of what the flag indicates
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    rule: str
    description: str

class AnalysisSuggestions(BaseModel):
    """
    Container for AI-generated suggestions.
    
    Attributes:
        derived_columns (List[DerivedColumn]): List of suggested derived columns
        flag_rules (List[FlagRule]): List of suggested flag rules
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    derived_columns: List[DerivedColumn]
    flag_rules: List[FlagRule]

class ProcessorState(BaseModel):
    """
    Maintains the state of the Excel processor.
    
    Attributes:
        column_history (List[dict]): History of applied column operations
        rule_history (List[str]): History of applied flag rules
        current_file (Optional[str]): Name of the currently loaded file
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    column_history: List[dict]
    rule_history: List[str]
    current_file: Optional[str] = None 