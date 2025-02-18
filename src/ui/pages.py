"""
Main page layouts and UI logic for the Streamlit application.
"""
import streamlit as st
from src.ui.components import show_example_operations, show_data_preview
from src.services.excel_processor import ExcelProcessor

def main_page():
    """Main page layout and logic"""
    st.set_page_config(
        page_title="Excel Data Processor",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Excel Data Processor")
    
    # Initialize session state
    if 'processor' not in st.session_state:
        st.session_state.processor = ExcelProcessor()
    
    # File upload section
    upload_section()
    
    # Only show other sections if data is loaded
    if st.session_state.processor.df is not None:
        data_preview_section()
        ai_assistant_section()
        derived_columns_section()
        flag_rules_section()
        results_section()

def upload_section():
    """File upload section"""
    st.header("1. Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file:
        if st.session_state.processor.load_excel(uploaded_file):
            st.success("File loaded successfully!")
        else:
            st.error("Failed to load file")

def data_preview_section():
    """Data preview section with row selection"""
    st.header("2. Data Preview")
    start_row, end_row = show_data_preview(st.session_state.processor)
    
    if st.button("Crop to Selection"):
        if st.session_state.processor.crop_selection(start_row, end_row):
            st.success("Data cropped successfully!")
            st.rerun()

def ai_assistant_section():
    """AI Assistant section for suggestions"""
    st.header("AI Assistant")
    show_example_operations()
    
    user_query = st.text_area(
        "Describe what columns or flags you want to create:",
        placeholder="e.g., 'Calculate total revenue by multiplying price and quantity'"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Try Example"):
            user_query = "Calculate total revenue by multiplying price and quantity, and flag items with revenue above $1000"
            st.session_state['user_query'] = user_query
            st.rerun()
            
    with col2:
        if st.button("Get Suggestions", type="primary"):
            if user_query:
                with st.spinner("Generating suggestions..."):
                    suggestions = st.session_state.processor.suggest_operations(user_query)
                    if suggestions:
                        st.session_state['suggestions'] = suggestions
                        st.rerun()
            else:
                st.warning("Please enter a query first")
    
    # Display suggestions
    if 'suggestions' in st.session_state:
        display_suggestions(st.session_state['suggestions'])

def derived_columns_section():
    """Section for creating derived columns"""
    st.header("3. Create Derived Columns")
    
    # Show available columns
    st.info("Available columns: " + ", ".join(st.session_state.processor.get_column_names()))
    
    # Column creation form
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        new_col_name = st.text_input("Column Name")
    with col2:
        formula = st.text_input("Formula (e.g., Price * Quantity)")
    with col3:
        if st.button("Add Column"):
            if new_col_name and formula:
                if st.session_state.processor.add_derived_column(new_col_name, formula):
                    st.success(f"Added column: {new_col_name}")
                    st.rerun()
    
    # Show created columns
    if st.session_state.processor.column_history:
        st.subheader("Created Columns")
        for idx, col in enumerate(st.session_state.processor.column_history):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.code(f"{col['name']} = {col['formula']}")
            with col2:
                if st.button("❌", key=f"remove_col_{idx}"):
                    st.session_state.processor.remove_derived_column(col['name'])
                    st.rerun()

def flag_rules_section():
    """Section for defining flag rules"""
    st.header("4. Define Flag Rules")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        rule = st.text_input("Rule (e.g., Price > 100)")
    with col2:
        if st.button("Add Rule"):
            if rule:
                if st.session_state.processor.add_flag_rule(rule):
                    st.success(f"Added flag rule: {rule}")
                    st.rerun()
    
    # Show applied rules
    if st.session_state.processor.rule_history:
        st.subheader("Applied Rules")
        for idx, rule in enumerate(st.session_state.processor.rule_history):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.code(rule)
            with col2:
                if st.button("❌", key=f"remove_rule_{idx}"):
                    st.session_state.processor.remove_flag_rule(rule)
                    st.rerun()

def results_section():
    """Final results section"""
    st.header("5. Processed Data")
    
    # Show column names
    st.write("Current columns:", st.session_state.processor.get_column_names())
    
    # Display DataFrame
    st.dataframe(st.session_state.processor.df)
    
    # Export button
    if st.download_button(
        label="Download Processed Data",
        data=st.session_state.processor.df.to_csv(index=False).encode('utf-8'),
        file_name="processed_data.csv",
        mime="text/csv"
    ):
        st.success("Data downloaded successfully!")

def display_suggestions(suggestions):
    """Display AI suggestions with apply buttons"""
    if suggestions.get("derived_columns"):
        st.subheader("Suggested Derived Columns")
        for idx, col in enumerate(suggestions["derived_columns"]):
            with st.expander(f"{col['name']}: {col['description']}"):
                st.write(f"Formula: `{col['formula']}`")
                if st.button("Apply", key=f"apply_col_{idx}"):
                    if st.session_state.processor.add_derived_column(col['name'], col['formula']):
                        st.success(f"Added column: {col['name']}")
                        st.rerun()
    
    if suggestions.get("flag_rules"):
        st.subheader("Suggested Flag Rules")
        for idx, flag in enumerate(suggestions["flag_rules"]):
            with st.expander(f"Flag: {flag['description']}"):
                st.write(f"Rule: `{flag['rule']}`")
                if st.button("Apply", key=f"apply_flag_{idx}"):
                    if st.session_state.processor.add_flag_rule(flag['rule']):
                        st.success(f"Added flag rule: {flag['rule']}")
                        st.rerun() 