"""
Test all Flask endpoints and routes using Flask Test Client.
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import app

def test_routes():
    print("Testing all application routes via Flask Test Client...")
    client = app.test_client()
    
    endpoints = [
        ('/', 200, "Dashboard root"),
        ('/dashboard', 200, "Dashboard route"),
        ('/upload', 200, "Upload page"),
        ('/analysis', 200, "Analysis page"),
        ('/prediction', 200, "Prediction page"),
        ('/recommendations', 200, "Recommendations page"),
        ('/bill-calculator', 200, "Bill calculator page"),
        ('/reports', 200, "Reports page"),
        ('/download/predictions-csv', 200, "Predictions CSV export"),
        ('/download/analyzed-csv', 200, "Analyzed data CSV export"),
        ('/download/report-pdf', 200, "Report PDF generation"),
        ('/download-sample-dataset', 200, "Sample dataset download"),
        ('/reset-dataset', 302, "Reset dataset redirect")
    ]
    
    all_passed = True
    for path, expected_status, description in endpoints:
        resp = client.get(path)
        if resp.status_code == expected_status:
            print(f" PASS: [{resp.status_code}] {description} ({path})")
            if 'csv' in path:
                print(f"       -> Data length: {len(resp.data)} bytes")
            elif 'pdf' in path:
                print(f"       -> PDF binary length: {len(resp.data)} bytes, Content-Type: {resp.content_type}")
        else:
            print(f" FAIL: Expected {expected_status} but got {resp.status_code} for {description} ({path})")
            all_passed = False
            
    # Test POST /update-tariff
    post_tariff = client.post('/update-tariff', data={'tariff_rate': '8.50'}, follow_redirects=True)
    if post_tariff.status_code == 200:
        print(" PASS: [200] POST /update-tariff followed redirect successfully")
    else:
        print(f" FAIL: POST /update-tariff returned {post_tariff.status_code}")
        all_passed = False
        
    if all_passed:
        print("\nALL FLASK ROUTES TESTED SUCCESSFULLY AND RETURNED EXPECTED STATUS CODES!")
    else:
        print("\nSOME ROUTE TESTS FAILED!")
        sys.exit(1)

if __name__ == '__main__':
    test_routes()
