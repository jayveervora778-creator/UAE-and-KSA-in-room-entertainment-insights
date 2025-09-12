#!/usr/bin/env python3
"""
Test for remaining dark elements in the dashboard
"""

import requests
import re
from pathlib import Path

def test_dark_elements():
    """Test if dark elements are eliminated"""
    
    print("🔍 Dark Element Detection Test")
    print("=" * 40)
    
    # Test dashboard response
    try:
        response = requests.get("https://8502-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev", timeout=15)
        
        if response.status_code == 200:
            print("✅ Dashboard accessible")
            
            # Check for light theme indicators
            light_indicators = [
                'background-color: #FFFFFF',
                'color: #374151',
                'plotly_white',
                'border: 2px solid #d1d5db'
            ]
            
            dark_indicators = [
                'background: #000',
                'background-color: #000',
                'color: #fff',
                'dark-theme',
                'theme-dark'
            ]
            
            print("\n🔍 Light Theme Indicators:")
            for indicator in light_indicators:
                if indicator in response.text:
                    print(f"   ✅ Found: {indicator}")
                else:
                    print(f"   ❌ Missing: {indicator}")
            
            print("\n🚫 Dark Theme Indicators:")
            dark_found = []
            for indicator in dark_indicators:
                if indicator in response.text:
                    dark_found.append(indicator)
                    print(f"   ⚠️ Found dark element: {indicator}")
            
            if not dark_found:
                print("   ✅ No dark theme indicators found!")
            
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
    
    # Test nuclear CSS file
    nuclear_file = Path(__file__).parent / 'nuclear_light_theme.py'
    if nuclear_file.exists():
        print(f"\n🎯 Nuclear Light Theme File:")
        print("   ✅ Nuclear light theme file exists")
        
        with open(nuclear_file, 'r') as f:
            content = f.read()
        
        nuclear_features = [
            'background: #FFFFFF !important',
            'color: #374151 !important', 
            '* {',
            'plotly',
            'stSelectbox'
        ]
        
        for feature in nuclear_features:
            if feature in content:
                print(f"   ✅ Nuclear feature: {feature}")
            else:
                print(f"   ❌ Missing feature: {feature}")
    else:
        print("   ❌ Nuclear light theme file not found")
    
    print("\n" + "=" * 40)
    print("🎯 Dark Element Test Complete!")
    print("\n🔗 Test the dashboard at:")
    print("https://8502-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev")
    print("\nIf you still see dark elements, try:")
    print("1. Hard refresh (Ctrl+Shift+R)")
    print("2. Clear browser cache")
    print("3. Try different browser")

if __name__ == "__main__":
    test_dark_elements()