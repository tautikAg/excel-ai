from setuptools import setup, find_packages

setup(
    name="excel_processor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.24.0',
        'pandas>=1.5.0',
        'numpy>=1.24.0',
        'litellm>=0.1.0',
        'python-dotenv>=0.19.0',
        'pydantic>=2.0.0'
    ],
) 