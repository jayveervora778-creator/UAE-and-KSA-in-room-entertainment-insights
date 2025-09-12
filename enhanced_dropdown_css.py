#!/usr/bin/env python3
"""
Enhanced CSS for dropdown boundaries and dark element fixes
"""

import streamlit as st

def apply_enhanced_css():
    """Apply enhanced CSS for dropdowns and light theme enforcement"""
    st.markdown("""
    <style>
        /* === AGGRESSIVE DARK MODE KILLER === */
        * {
            background-color: inherit !important;
            color: inherit !important;
        }
        
        /* Force all possible selectors to light theme */
        div, span, input, select, button, ul, li, p, h1, h2, h3, h4, h5, h6 {
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === COMPREHENSIVE DROPDOWN FIXES === */
        /* Target ALL Streamlit select components */
        [class*="st-"],
        [class*="Select"],
        [data-baseweb*="select"],
        [data-testid*="select"],
        [class*="dropdown"],
        [class*="menu"] {
            background-color: #FFFFFF !important;
            color: #374151 !important;
            border: 1px solid #d1d5db !important;
        }
        /* === ENHANCED DROPDOWN BOUNDARIES === */
        .stSelectbox > div > div {
            background-color: #FFFFFF !important;
            border: 2px solid #d1d5db !important;
            border-radius: 6px !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #667eea !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }
        
        /* === DROPDOWN LIST STYLING === */
        [data-baseweb="menu"] {
            background-color: #FFFFFF !important;
            border: 2px solid #d1d5db !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            max-height: 200px !important;
            overflow-y: auto !important;
        }
        
        [data-baseweb="menu"] > ul {
            background-color: #FFFFFF !important;
            padding: 4px !important;
        }
        
        [data-baseweb="menu"] li {
            background-color: #FFFFFF !important;
            color: #374151 !important;
            padding: 8px 12px !important;
            border-radius: 4px !important;
            margin: 2px 0 !important;
            cursor: pointer !important;
        }
        
        [data-baseweb="menu"] li:hover {
            background-color: #f3f4f6 !important;
            color: #1f2937 !important;
        }
        
        [data-baseweb="menu"] li[aria-selected="true"] {
            background-color: #667eea !important;
            color: #FFFFFF !important;
        }
        
        /* === FORCE ALL ELEMENTS LIGHT === */
        * {
            color: inherit !important;
        }
        
        div[class*="css"] {
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === SIDEBAR ENHANCEMENTS === */
        .stSidebar .stSelectbox > div > div {
            background-color: #FFFFFF !important;
            border: 2px solid #d1d5db !important;
            border-radius: 6px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stSidebar .stSelectbox > div > div:hover {
            border-color: #667eea !important;
        }
        
        /* === MULTISELECT ENHANCEMENTS === */
        .stMultiSelect > div > div {
            background-color: #FFFFFF !important;
            border: 2px solid #d1d5db !important;
            border-radius: 6px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* === TAB ENHANCEMENTS === */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f9fafb !important;
            border-bottom: 2px solid #e5e7eb !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #FFFFFF !important;
            color: #6b7280 !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 6px 6px 0 0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #667eea !important;
            color: #FFFFFF !important;
        }
        
        /* === COMPREHENSIVE DARK MODE PREVENTION === */
        [data-testid="stSelectbox"] > div,
        [data-testid="stSelectbox"] > div > div {
            background-color: #FFFFFF !important;
            border: 2px solid #d1d5db !important;
            border-radius: 6px !important;
        }
        
        /* Tooltip and popup elements */
        [role="tooltip"],
        [role="dialog"],
        [role="menu"],
        [role="listbox"] {
            background-color: #FFFFFF !important;
            color: #374151 !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
    </style>
    """, unsafe_allow_html=True)