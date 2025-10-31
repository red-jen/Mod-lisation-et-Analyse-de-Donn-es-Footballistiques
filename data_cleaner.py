"""
Data cleaning and transformation utilities
"""

import pandas as pd

def clean_players(df):
    """Clean players DataFrame"""
    df = df.drop_duplicates()
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df = df.dropna(subset=['player'])
    return df

def clean_matches(df):
    """Clean matches DataFrame"""
    df = df.drop_duplicates()
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    df = df.dropna(subset=['date'])
    
    numeric_cols = ['gf', 'ga', 'xg', 'xga', 'poss']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def standardize_columns(df):
    """Standardize column names"""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df
