#!/usr/bin/env python3
"""
Refined Light Theme - Beautiful UI with subtle design elements
"""

import streamlit as st

def apply_refined_light_theme():
    """Apply refined, elegant light theme with subtle design elements"""
    st.markdown("""
    <style>
        /* === REFINED LIGHT THEME === */
        /* Global light enforcement without harsh borders */
        * {
            color: inherit !important;
        }
        
        /* Root theme variables */
        :root {
            --background-primary: #FFFFFF;
            --background-secondary: #f8fafc;
            --background-accent: #f1f5f9;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --text-muted: #9ca3af;
            --border-subtle: #e5e7eb;
            --border-light: #f3f4f6;
            --border-focus: #94a3b8;
            --shadow-subtle: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-medium: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-card: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --radius-sm: 4px;
            --radius-md: 6px;
            --radius-lg: 8px;
            --radius-xl: 12px;
        }
        
        /* === APP CONTAINER === */
        .stApp {
            background-color: var(--background-primary) !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            background-color: var(--background-primary) !important;
            color: var(--text-primary) !important;
            padding-top: 2rem !important;
        }
        
        /* === ELEGANT SIDEBAR === */
        .stSidebar {
            background-color: var(--background-secondary) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }
        
        .stSidebar .stSelectbox > label,
        .stSidebar .stMultiSelect > label {
            color: var(--text-primary) !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* === REFINED DROPDOWNS === */
        .stSelectbox > div > div {
            background-color: var(--background-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-subtle) !important;
            padding: 0.5rem 0.75rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: var(--border-focus) !important;
            box-shadow: var(--shadow-medium) !important;
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: #94a3b8 !important;
            box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.2) !important;
        }
        
        /* Dropdown text */
        .stSelectbox > div > div > div {
            color: var(--text-primary) !important;
            background-color: transparent !important;
        }
        
        /* === MULTI-SELECT STYLING === */
        .stMultiSelect > div > div {
            background-color: var(--background-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-subtle) !important;
            min-height: 2.5rem !important;
        }
        
        .stMultiSelect > div > div:hover {
            border-color: var(--border-focus) !important;
            box-shadow: var(--shadow-medium) !important;
        }
        
        /* === ELEGANT BUTTONS === */
        .stButton > button {
            background-color: var(--border-focus) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            box-shadow: var(--shadow-subtle) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            background-color: #2563eb !important;
            box-shadow: var(--shadow-medium) !important;
            transform: translateY(-1px) !important;
        }
        
        /* === TEXT INPUTS === */
        .stTextInput > div > div > input {
            background-color: var(--background-primary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.5rem 0.75rem !important;
            box-shadow: var(--shadow-subtle) !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #94a3b8 !important;
            box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.2) !important;
        }
        
        /* === REFINED EXPANDERS === */
        .streamlit-expanderHeader {
            background-color: var(--background-secondary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
        }
        
        .streamlit-expanderContent {
            background-color: var(--background-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-top: none !important;
            border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
        }
        
        /* === METRICS CARDS === */
        .stMetric {
            background-color: var(--background-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            padding: 1rem !important;
            box-shadow: var(--shadow-subtle) !important;
        }
        
        .stMetric > div {
            color: var(--text-primary) !important;
        }
        
        /* === DATAFRAMES === */
        .stDataFrame {
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden !important;
        }
        
        .stDataFrame table {
            background-color: var(--background-primary) !important;
        }
        
        .stDataFrame th {
            background-color: var(--background-secondary) !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            border-bottom: 1px solid var(--border-subtle) !important;
        }
        
        .stDataFrame td {
            background-color: var(--background-primary) !important;
            color: var(--text-primary) !important;
            border-bottom: 1px solid var(--border-subtle) !important;
        }
        
        /* === CHARTS === */
        .stPlotlyChart {
            background-color: var(--background-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            box-shadow: var(--shadow-subtle) !important;
            padding: 0.5rem !important;
        }
        
        /* === TYPOGRAPHY === */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
        }
        
        p, span, div {
            color: var(--text-secondary) !important;
        }
        
        /* Widget labels */
        .stSelectbox label,
        .stMultiSelect label,
        .stTextInput label,
        .stSlider label {
            color: var(--text-primary) !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* === ALERT MESSAGES === */
        .stAlert {
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--border-subtle) !important;
            box-shadow: var(--shadow-subtle) !important;
        }
        
        .stSuccess {
            background-color: #f0fdf4 !important;
            border-color: #bbf7d0 !important;
            color: #166534 !important;
        }
        
        .stInfo {
            background-color: #eff6ff !important;
            border-color: #bfdbfe !important;
            color: #1e40af !important;
        }
        
        .stWarning {
            background-color: #fffbeb !important;
            border-color: #fed7aa !important;
            color: #92400e !important;
        }
        
        .stError {
            background-color: #fef2f2 !important;
            border-color: #fecaca !important;
            color: #dc2626 !important;
        }
        
        /* === COMPREHENSIVE DROPDOWN TARGETING === */
        /* Target ALL possible dropdown containers */
        [data-baseweb="menu"],
        [role="listbox"],
        [role="menu"],
        .css-26l3qy-menu,
        .css-1nmdiq5-menu,
        div[class*="menu"],
        div[class*="Menu"],
        div[class*="dropdown"],
        div[class*="Dropdown"],
        ul[role="listbox"] {
            background-color: var(--background-primary) !important;
            background: var(--background-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
            padding: 0.25rem !important;
            color: var(--text-primary) !important;
        }
        
        /* Target ALL possible dropdown options */
        [data-baseweb="menu"] li,
        [role="option"],
        .css-1n7v3ny-option,
        .css-yt9ioa-option,
        .css-9gakcf-option,
        li[role="option"],
        div[role="option"],
        ul[role="listbox"] > li,
        div[class*="option"],
        div[class*="Option"] {
            background-color: transparent !important;
            background: transparent !important;
            color: var(--text-primary) !important;
            padding: 0.5rem 0.75rem !important;
            border-radius: var(--radius-sm) !important;
            margin: 0.125rem 0 !important;
            transition: background-color 0.15s ease !important;
            border: none !important;
        }
        
        /* Hover states for options */
        [data-baseweb="menu"] li:hover,
        [role="option"]:hover,
        .css-1n7v3ny-option:hover,
        .css-yt9ioa-option:hover,
        .css-9gakcf-option:hover,
        li[role="option"]:hover,
        div[role="option"]:hover,
        div[class*="option"]:hover {
            background-color: var(--background-secondary) !important;
            background: var(--background-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Selected states */
        [data-baseweb="menu"] li[aria-selected="true"],
        [role="option"][aria-selected="true"],
        .css-1n7v3ny-option[aria-selected="true"],
        li[role="option"][aria-selected="true"],
        div[role="option"][aria-selected="true"],
        div[class*="option"][aria-selected="true"] {
            background-color: var(--border-focus) !important;
            background: var(--border-focus) !important;
            color: white !important;
        }
        
        /* === AGGRESSIVE REACT-SELECT TARGETING === */
        /* Target React Select CSS classes that might appear */
        .css-1s2u09g-control,
        .css-1pahdxg-control,
        .css-13cymwt-control,
        .css-t3ipsp-control,
        .css-1hwfws3,
        .css-1wa3eu0-placeholder,
        .css-1uccc91-singleValue,
        .css-15lsz6c-indicatorContainer {
            background-color: var(--background-primary) !important;
            background: var(--background-primary) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-subtle) !important;
        }
        
        /* === STREAMLIT SPECIFIC OVERRIDES === */
        /* Force light theme on any Streamlit widget that might be dark */
        div[data-testid*="select"],
        div[data-testid*="Select"],
        div[class*="st-"],
        span[class*="st-"],
        .stSelectbox *,
        .stMultiSelect * {
            background-color: var(--background-primary) !important;
            background: var(--background-primary) !important;
            color: var(--text-primary) !important;
        }
        
        /* === TABS === */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--background-secondary) !important;
            border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
            padding: 0.25rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: var(--text-secondary) !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
            padding: 0.5rem 1rem !important;
            margin: 0 0.125rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: var(--background-primary) !important;
            color: var(--text-primary) !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--background-primary) !important;
            color: var(--border-focus) !important;
            box-shadow: var(--shadow-subtle) !important;
        }
        
        /* === SCROLLBARS === */
        ::-webkit-scrollbar {
            width: 6px !important;
            height: 6px !important;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--background-secondary) !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-subtle) !important;
            border-radius: 3px !important;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary) !important;
        }
        
        /* === REMOVE HARSH ELEMENTS === */
        /* Hide Streamlit branding */
        .stDeployButton {display: none !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        
        /* Remove any remaining thick borders */
        * {
            border-width: 1px !important;
        }
        
        /* Ensure light backgrounds for all components */
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stSidebar"],
        [data-testid="stToolbar"] {
            background-color: var(--background-primary) !important;
        }
        
        /* === FINAL DARK ELEMENT KILLER === */
        /* Force light background on ANY element with dark styling */
        [style*="background-color: rgb(38"],
        [style*="background-color: rgb(17"],
        [style*="background-color: rgb(30"],
        [style*="background: rgb(38"],
        [style*="background: rgb(17"],
        [style*="background: rgb(30"],
        [class*="dark"],
        [class*="Dark"],
        [data-theme="dark"] {
            background-color: var(--background-primary) !important;
            background: var(--background-primary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Universal dropdown override - catch any missed elements */
        ul[role="listbox"] li,
        div[role="option"],
        span[role="option"],
        * > ul > li,
        * > div[role="option"] {
            background-color: var(--background-primary) !important;
            background: var(--background-primary) !important;
            color: var(--text-primary) !important;
        }
    </style>
    """, unsafe_allow_html=True)