#!/usr/bin/env python3
"""
Complete end-to-end test for the OSN Survey Dashboard
Tests login, API endpoints, and data format
"""

import requests
import json
import sys

BASE_URL = 'https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev'

def test_login():
    """Test login functionality"""
    print("🔐 Testing login...")
    
    session = requests.Session()
    
    # Test login
    login_data = {
        'username': 'admin',
        'password': 'surveydash2024'
    }
    
    response = session.post(f'{BASE_URL}/login', json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Login successful")
            return session
        else:
            print(f"❌ Login failed: {data.get('message')}")
            return None
    else:
        print(f"❌ Login request failed: {response.status_code}")
        return None

def test_dynamic_charts(session):
    """Test dynamic charts API"""
    print("\n📊 Testing dynamic charts API...")
    
    response = session.get(f'{BASE_URL}/enhanced_api/dynamic-charts')
    
    if response.status_code == 200:
        data = response.json()
        
        if 'charts' in data and len(data['charts']) > 0:
            print(f"✅ Charts API working - {len(data['charts'])} charts found")
            
            # Test chart format
            chart_names = list(data['charts'].keys())
            sample_chart = data['charts'][chart_names[0]]
            
            print(f"📋 Sample chart: {chart_names[0]}")
            
            # Check Chart.js format
            if 'data' in sample_chart:
                chart_data = sample_chart['data']
                
                # Check for proper Chart.js format
                has_labels = 'labels' in chart_data
                has_datasets = 'datasets' in chart_data
                
                if has_labels and has_datasets:
                    print("✅ Chart format is correct (labels + datasets)")
                    return data
                else:
                    print(f"❌ Chart format incorrect - labels: {has_labels}, datasets: {has_datasets}")
                    return None
            else:
                print("❌ Chart missing data property")
                return None
        else:
            print("❌ No charts found in response")
            return None
    else:
        print(f"❌ Charts API failed: {response.status_code}")
        return None

def test_survey_insights(session):
    """Test survey insights API"""
    print("\n🧠 Testing survey insights API...")
    
    response = session.get(f'{BASE_URL}/enhanced_api/survey-insights')
    
    if response.status_code == 200:
        data = response.json()
        
        if 'key_findings' in data and len(data['key_findings']) > 0:
            print(f"✅ Survey insights working - {len(data['key_findings'])} findings")
            
            # Check first finding structure
            first_finding = data['key_findings'][0]
            required_fields = ['title', 'finding', 'data_backing', 'rationale']
            
            missing_fields = [field for field in required_fields if field not in first_finding]
            
            if not missing_fields:
                print("✅ Survey insights have proper structure")
                return True
            else:
                print(f"❌ Survey insights missing fields: {missing_fields}")
                return False
        else:
            print("❌ No survey insights found")
            return False
    else:
        print(f"❌ Survey insights API failed: {response.status_code}")
        return False

def test_filtering(session):
    """Test filtering functionality"""
    print("\n🔍 Testing filtering functionality...")
    
    # Test with UAE filter
    params = {'country': 'UAE'}
    response = session.get(f'{BASE_URL}/enhanced_api/dynamic-charts', params=params)
    
    if response.status_code == 200:
        uae_data = response.json()
        
        # Test with KSA filter
        params = {'country': 'KSA'}
        response = session.get(f'{BASE_URL}/enhanced_api/dynamic-charts', params=params)
        
        if response.status_code == 200:
            ksa_data = response.json()
            
            # Check if filtering produces different chart labels (better test than response count)
            uae_chart = uae_data.get('charts', {}).get('entertainment_importance_by_country', {})
            ksa_chart = ksa_data.get('charts', {}).get('entertainment_importance_by_country', {})
            
            uae_labels = uae_chart.get('data', {}).get('labels', [])
            ksa_labels = ksa_chart.get('data', {}).get('labels', [])
            
            if uae_labels == ['UAE'] and ksa_labels == ['KSA']:
                print(f"✅ Filtering working - UAE shows: {uae_labels}, KSA shows: {ksa_labels}")
                
                # Also check response counts
                uae_responses = uae_data.get('metadata', {}).get('total_responses', 0)
                ksa_responses = ksa_data.get('metadata', {}).get('total_responses', 0)
                print(f"📊 Response counts - UAE: {uae_responses}, KSA: {ksa_responses}")
                
                return True
            else:
                print(f"❌ Filtering not working - UAE labels: {uae_labels}, KSA labels: {ksa_labels}")
                return False
        else:
            print("❌ KSA filter failed")
            return False
    else:
        print("❌ UAE filter failed")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting OSN Survey Dashboard End-to-End Tests\n")
    
    # Test 1: Login
    session = test_login()
    if not session:
        print("\n❌ FAILED: Cannot proceed without login")
        return False
    
    # Test 2: Dynamic Charts
    chart_data = test_dynamic_charts(session)
    if not chart_data:
        print("\n❌ FAILED: Charts not working")
        return False
    
    # Test 3: Survey Insights
    insights_ok = test_survey_insights(session)
    if not insights_ok:
        print("\n❌ FAILED: Survey insights not working")
        return False
    
    # Test 4: Filtering
    filtering_ok = test_filtering(session)
    if not filtering_ok:
        print("\n❌ FAILED: Filtering not working")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("\n📋 Summary:")
    print("✅ Login functionality working")
    print("✅ Dynamic charts API working") 
    print("✅ Chart format correct for Chart.js")
    print("✅ Survey insights with data rationale working")
    print("✅ Filtering functionality working")
    print("\n🔗 Dashboard URL: https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev")
    print("🔑 Login: admin / surveydash2024")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)