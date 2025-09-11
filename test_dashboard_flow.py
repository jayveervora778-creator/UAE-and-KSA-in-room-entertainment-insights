#!/usr/bin/env python3
"""
Test the complete dashboard flow including login and Chart.js loading
"""
import requests
import json
from urllib.parse import urljoin

BASE_URL = 'https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev'

def test_complete_flow():
    """Test login and dashboard access"""
    session = requests.Session()
    
    print("🔐 Step 1: Testing login...")
    
    # Login
    login_response = session.post(f'{BASE_URL}/login', json={
        'username': 'admin',
        'password': 'surveydash2024'
    })
    
    if login_response.status_code == 200 and login_response.json().get('success'):
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return False
    
    print("\n📊 Step 2: Testing dashboard access...")
    
    # Access dashboard
    dashboard_response = session.get(f'{BASE_URL}/simple-dashboard')
    
    if dashboard_response.status_code == 200:
        print("✅ Dashboard accessible")
        html_content = dashboard_response.text
        
        # Check key elements
        checks = {
            'Chart.js script': 'chart.js' in html_content.lower() or 'chart.min.js' in html_content.lower(),
            'Filter dropdowns': 'countryFilter' in html_content and 'purposeFilter' in html_content,
            'Charts container': 'chartsContainer' in html_content,
            'Bootstrap': 'bootstrap' in html_content.lower(),
            'FontAwesome': 'fontawesome' in html_content.lower(),
        }
        
        print("\n🔍 Dashboard components:")
        for component, present in checks.items():
            status = "✅" if present else "❌"
            print(f"  {status} {component}: {'Present' if present else 'Missing'}")
        
        return all(checks.values())
    else:
        print(f"❌ Dashboard not accessible: {dashboard_response.status_code}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    session = requests.Session()
    
    # Login first
    session.post(f'{BASE_URL}/login', json={'username': 'admin', 'password': 'surveydash2024'})
    
    print("\n🔗 Step 3: Testing API endpoints...")
    
    endpoints = {
        'Charts API': '/enhanced_api/dynamic-charts',
        'Survey Insights': '/enhanced_api/survey-insights'
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            response = session.get(f'{BASE_URL}{endpoint}')
            if response.status_code == 200:
                data = response.json()
                
                if endpoint == '/enhanced_api/dynamic-charts':
                    chart_count = len(data.get('charts', {}))
                    results[name] = f"✅ Working - {chart_count} charts"
                elif endpoint == '/enhanced_api/survey-insights':
                    findings_count = len(data.get('key_findings', []))
                    results[name] = f"✅ Working - {findings_count} findings"
                else:
                    results[name] = "✅ Working"
            else:
                results[name] = f"❌ Failed - {response.status_code}"
        except Exception as e:
            results[name] = f"❌ Error - {str(e)}"
    
    for name, result in results.items():
        print(f"  {result}: {name}")
    
    return all("✅" in result for result in results.values())

if __name__ == '__main__':
    print("🧪 OSN Dashboard Complete Flow Test\n")
    
    dashboard_ok = test_complete_flow()
    api_ok = test_api_endpoints()
    
    print(f"\n📊 Test Results:")
    print(f"Dashboard Components: {'✅ PASS' if dashboard_ok else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if dashboard_ok and api_ok:
        print(f"\n🎉 All components working!")
        print(f"\n🔗 Dashboard URL: {BASE_URL}")
        print("📝 Login: admin / surveydash2024")
        print("\n💡 The dashboard should now work properly in browser")
    else:
        print(f"\n❌ Some components need fixing")