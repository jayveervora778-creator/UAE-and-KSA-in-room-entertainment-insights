#!/usr/bin/env python3
"""
Test script to verify enhanced UI improvements
"""

import requests
import re
from pathlib import Path

def test_enhanced_css():
    """Test if enhanced CSS is properly applied"""
    
    print("🎨 Enhanced UI Test Report")
    print("=" * 40)
    
    # 1. Check if enhanced CSS file exists
    css_file = Path(__file__).parent / 'enhanced_dropdown_css.py'
    if css_file.exists():
        print("✅ Enhanced CSS file exists")
        
        # Check CSS content
        with open(css_file, 'r') as f:
            content = f.read()
            
        css_features = {
            'Dropdown borders': 'border: 2px solid #d1d5db',
            'Hover effects': ':hover',
            'Focus states': ':focus-within',
            'Light backgrounds': 'background-color: #FFFFFF',
            'Box shadows': 'box-shadow:',
            'Border radius': 'border-radius:'
        }
        
        print("\n🔍 CSS Features Check:")
        for feature, pattern in css_features.items():
            if pattern in content:
                print(f"   ✅ {feature}: Applied")
            else:
                print(f"   ❌ {feature}: Missing")
    else:
        print("❌ Enhanced CSS file not found")
    
    # 2. Check main Streamlit app integration
    app_file = Path(__file__).parent / 'streamlit_app.py'
    if app_file.exists():
        print(f"\n📱 Streamlit Integration:")
        
        with open(app_file, 'r') as f:
            app_content = f.read()
        
        integration_checks = {
            'Enhanced CSS import': 'from enhanced_dropdown_css import apply_enhanced_css',
            'CSS function call': 'apply_enhanced_css()',
            'Original CSS base': 'Enhanced CSS - Force Light Mode',
            'Dropdown styling': 'stSelectbox'
        }
        
        for check, pattern in integration_checks.items():
            if pattern in app_content:
                print(f"   ✅ {check}: Found")
            else:
                print(f"   ❌ {check}: Missing")
    
    # 3. Test dashboard accessibility
    try:
        print(f"\n🌐 Dashboard Accessibility:")
        response = requests.get("https://8502-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev", timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Dashboard accessible (HTTP {response.status_code})")
            
            # Check for CSS in response
            if 'background-color: #FFFFFF' in response.text:
                print("   ✅ Light theme CSS detected in response")
            else:
                print("   ⚠️ Light theme CSS not found in response")
                
            if 'stSelectbox' in response.text:
                print("   ✅ Dropdown elements detected")
            else:
                print("   ⚠️ Dropdown elements not found")
        else:
            print(f"   ❌ Dashboard not accessible (HTTP {response.status_code})")
            
    except requests.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Enhanced UI Test Complete!")
    
    print(f"\n🔗 Access the enhanced dashboard at:")
    print(f"https://8502-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev")

if __name__ == "__main__":
    test_enhanced_css()