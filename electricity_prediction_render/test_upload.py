"""
Test Upload functionality: valid CSV upload, invalid file type, missing columns.
"""
import io
import sys
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import app

def test_upload():
    client = app.test_client()
    
    # 1. Test uploading invalid file extension
    data = {'file': (io.BytesIO(b"some content"), 'test.txt')}
    resp = client.post('/upload-dataset', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200
    assert b"Invalid file format" in resp.data
    print(" PASS: Rejected non-CSV upload with error message")

    # 2. Test uploading CSV with missing required columns
    bad_csv = io.BytesIO(b"colA,colB\n1,2\n3,4")
    data = {'file': (bad_csv, 'bad.csv')}
    resp = client.post('/upload-dataset', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200
    assert b"Missing required columns" in resp.data
    print(" PASS: Rejected CSV missing required columns with clear error message")

    # 3. Test uploading valid custom CSV (72 sequential hours)
    dates = pd.date_range("2025-01-01 00:00:00", periods=72, freq="h")
    valid_csv = "datetime,consumption_kwh\n"
    for i, dt in enumerate(dates):
        valid_csv += f"{dt.strftime('%Y-%m-%d %H:%M:%S')},{round(2.5 + (i%6)*0.4, 2)}\n"
        
    data = {'file': (io.BytesIO(valid_csv.encode('utf-8')), 'custom_meter.csv')}
    resp = client.post('/upload-dataset', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dataset successfully uploaded and validated" in resp.data
    print(" PASS: Valid custom CSV uploaded, validated, cleaned, and model retrained!")

if __name__ == '__main__':
    test_upload()
