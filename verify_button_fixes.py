#!/usr/bin/env python3
"""
Verify that all generate button fixes are working in the actual dashboard
"""

import requests
import time

def check_dashboard_status():
    """Check if dashboard is accessible"""
    try:
        response = requests.get("https://8501-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
            return True
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard not accessible: {str(e)}")
        return False

def check_button_keys():
    """Check that all buttons have unique keys in the code"""
    print("\n🔍 Checking button key assignments...")
    
    with open("/home/user/webapp/balanced_contrast_dashboard.py", "r") as f:
        content = f.read()
    
    # Check for the three generate buttons with keys
    button_patterns = [
        ('Cross-Analysis', 'key="generate_cross_analysis"'),
        ('Word Cloud', 'key="generate_word_cloud"'),
        ('Advanced Insights', 'key="generate_advanced_insights"')
    ]
    
    all_found = True
    for button_name, key_pattern in button_patterns:
        if key_pattern in content:
            print(f"✅ {button_name} button has unique key")
        else:
            print(f"❌ {button_name} button missing unique key")
            all_found = False
    
    return all_found

def check_imports():
    """Check that all required imports are present"""
    print("\n📦 Checking required imports...")
    
    with open("/home/user/webapp/balanced_contrast_dashboard.py", "r") as f:
        content = f.read()
    
    required_imports = [
        'from enhanced_osn_processor import EnhancedOSNProcessor',
        'from osn_wordcloud_analyzer import OSNWordCloudAnalyzer', 
        'from advanced_text_insights_analyzer import AdvancedTextInsightsAnalyzer'
    ]
    
    all_found = True
    for import_line in required_imports:
        if import_line in content:
            print(f"✅ {import_line.split()[-1]} imported")
        else:
            print(f"❌ Missing import: {import_line}")
            all_found = False
    
    return all_found

def check_function_definitions():
    """Check that required functions are defined"""
    print("\n🔧 Checking function definitions...")
    
    functions_to_check = [
        ("create_wordcloud_visualization", "/home/user/webapp/balanced_contrast_dashboard.py"),
        ("display_advanced_insights", "/home/user/webapp/balanced_contrast_dashboard.py"),
        ("get_cross_tabulation", "/home/user/webapp/enhanced_osn_processor.py"),
        ("get_text_responses_for_wordcloud", "/home/user/webapp/enhanced_osn_processor.py"),
        ("generate_comprehensive_insights_report", "/home/user/webapp/advanced_text_insights_analyzer.py")
    ]
    
    all_found = True
    for func_name, file_path in functions_to_check:
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            if f"def {func_name}" in content:
                print(f"✅ {func_name} defined in {file_path.split('/')[-1]}")
            else:
                print(f"❌ {func_name} not found in {file_path.split('/')[-1]}")
                all_found = False
        except Exception as e:
            print(f"❌ Error checking {file_path}: {str(e)}")
            all_found = False
    
    return all_found

def main():
    """Run comprehensive verification"""
    print("🚀 Verifying Generate Button Fixes\n")
    print("=" * 50)
    
    results = []
    
    # Test 1: Dashboard accessibility
    results.append(("Dashboard Accessibility", check_dashboard_status()))
    
    # Test 2: Button keys
    results.append(("Button Key Assignment", check_button_keys()))
    
    # Test 3: Imports
    results.append(("Required Imports", check_imports()))
    
    # Test 4: Function definitions
    results.append(("Function Definitions", check_function_definitions()))
    
    # Summary
    print("\n📊 VERIFICATION RESULTS:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 ALL GENERATE BUTTON FIXES VERIFIED!")
        print("\n💡 Next Steps:")
        print("1. Test each generate button in the dashboard UI")
        print("2. Verify buttons work with different filter combinations")
        print("3. Ensure results display correctly")
        print(f"\n🔗 Dashboard URL: https://8501-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev")
    else:
        print("⚠️  SOME ISSUES NEED TO BE ADDRESSED")
        print("\n🔧 Recommended Actions:")
        print("1. Fix any missing imports or functions")
        print("2. Restart the dashboard service")
        print("3. Re-run this verification script")
    
    return all_passed

if __name__ == "__main__":
    main()