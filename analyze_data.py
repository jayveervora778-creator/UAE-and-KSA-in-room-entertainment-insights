#!/usr/bin/env python3
"""
Script to analyze the structure of the survey Excel file
"""
import pandas as pd
import numpy as np
from pathlib import Path

def analyze_excel_file(filepath):
    """Analyze the structure and content of the Excel file"""
    print("=" * 80)
    print("SURVEY DATA ANALYSIS")
    print("=" * 80)
    
    try:
        # Get all sheet names
        xl = pd.ExcelFile(filepath)
        print(f"Excel file sheets: {xl.sheet_names}")
        print()
        
        # Analyze each sheet
        for sheet_name in xl.sheet_names:
            print(f"SHEET: {sheet_name}")
            print("-" * 40)
            
            # Read the sheet
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print()
            
            # Display basic info
            print("Column Info:")
            for i, col in enumerate(df.columns):
                dtype = str(df[col].dtype)
                non_null = df[col].count()
                null_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                print(f"  {i+1:2d}. {col:<30} | Type: {dtype:<10} | Non-null: {non_null:<4} | Null: {null_count:<4} | Unique: {unique_count}")
            
            print()
            
            # Show first few rows
            print("First 3 rows:")
            print(df.head(3).to_string())
            print()
            
            # Identify potential text response columns
            text_columns = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Check if column contains longer text (potential responses)
                    sample_values = df[col].dropna().head(10)
                    avg_length = sample_values.astype(str).str.len().mean()
                    if avg_length > 20:  # Assume text responses are longer than 20 characters
                        text_columns.append(col)
            
            if text_columns:
                print("Potential text response columns:")
                for col in text_columns:
                    print(f"  - {col}")
                    sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else "No data"
                    print(f"    Sample: {str(sample)[:100]}...")
                print()
            
            # Identify categorical columns (country, nationality, etc.)
            categorical_columns = []
            for col in df.columns:
                if df[col].dtype == 'object' and col not in text_columns:
                    unique_count = df[col].nunique()
                    if 1 < unique_count <= 50:  # Reasonable range for categories
                        categorical_columns.append((col, unique_count))
            
            if categorical_columns:
                print("Potential categorical columns for filtering:")
                for col, unique_count in categorical_columns:
                    print(f"  - {col} ({unique_count} unique values)")
                    unique_vals = df[col].dropna().unique()[:5]  # Show first 5 unique values
                    print(f"    Sample values: {list(unique_vals)}")
                print()
            
            print("=" * 80)
            print()
    
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    filepath = "survey_data.xlsx"
    if Path(filepath).exists():
        analyze_excel_file(filepath)
    else:
        print(f"File {filepath} not found!")