#!/usr/bin/env python3
"""
Simple test script to check if light mode CSS is working
"""
import streamlit as st

st.set_page_config(page_title="Light Mode Test", layout="wide")

# Test CSS
st.markdown("""
<style>
    .test-element {
        background-color: #FFFFFF;
        color: #262730;
        padding: 10px;
        border: 1px solid #ddd;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Light Mode Test")
st.write("This page tests if all elements are in light mode.")

col1, col2 = st.columns(2)

with col1:
    st.selectbox("Test Selectbox", ["Option 1", "Option 2", "Option 3"])
    st.text_input("Test Text Input", "Sample text")
    st.button("Test Button")

with col2:
    st.markdown('<div class="test-element">Custom styled element</div>', unsafe_allow_html=True)
    st.info("Info message")
    st.success("Success message")
    st.warning("Warning message")

# Test if elements appear with light backgrounds
st.markdown("### All elements above should have light/white backgrounds")