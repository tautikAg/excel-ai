"""
Reusable UI components for the Streamlit interface.
"""
import streamlit as st

def show_example_operations():
    """Display example operations in an expander"""
    with st.expander("See example operations you can request"):
        st.markdown("""
        **Example requests you can try:**
        
        1. "Calculate total revenue by multiplying price and quantity, and flag items with revenue above $1000"
        2. "Create a discount column that's 10% of the price, and flag items where quantity is less than 5"
        3. "Add a profit margin column that's 20% of the price, and flag items where margin is below $10"
        4. "Create a shipping cost column based on weight (weight * 2), and flag heavy items above 50kg"
        5. "Calculate price per unit by dividing total price by quantity, and flag items where unit price > $100"
        """)

def show_data_preview(processor):
    """Display data preview with row selection"""
    st.subheader("Data Preview")
    st.write("Select rows by dragging the slider:")
    
    row_count = len(processor.df)
    start_row, end_row = st.select_slider(
        "Select row range",
        options=range(row_count),
        value=(0, row_count-1),
        key="row_range"
    )
    
    preview_df = processor.df.iloc[start_row:end_row+1]
    st.dataframe(preview_df)
    return start_row, end_row 