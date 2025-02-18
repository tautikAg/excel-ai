import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)

# Create sample data
data = {
    'Product_ID': [f'P{i:03d}' for i in range(1, 11)],
    'Product_Name': [
        'Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Keyboard',
        'Mouse', 'Headphones', 'Printer', 'Scanner', 'Speaker'
    ],
    'Category': [
        'Electronics', 'Mobile', 'Mobile', 'Electronics', 'Accessories',
        'Accessories', 'Audio', 'Office', 'Office', 'Audio'
    ],
    'Price': np.random.uniform(100, 1000, 10).round(2),
    'Quantity': np.random.randint(10, 100, 10),
    'Supplier': [
        'TechCorp', 'MobilePro', 'TabletCo', 'ScreenTech', 'PeriphCo',
        'PeriphCo', 'AudioTech', 'PrintPro', 'ScanCo', 'SoundTech'
    ],
    'In_Stock': [random.choice([True, False]) for _ in range(10)],
    'Last_Restock_Date': pd.date_range(start='2024-01-01', periods=10)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('sample_inventory.xlsx', index=False) 