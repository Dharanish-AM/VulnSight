import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("🚀 Starting End-to-End System Test...")
    
    # 1. Start Scan
    target = "scanme.nmap.org"
    print(f"📡 Initiating scan for target: {target}")
    try:
        resp = requests.post(f"{BASE_URL}/scan/start", json={"target": target})
        resp.raise_for_status()
        scan_id = resp.json()["scan_id"]
        print(f"✅ Scan started. ID: {scan_id}")
    except Exception as e:
        print(f"❌ Failed to start scan: {e}")
        return

    # 2. Poll Status
    print("⏳ Polling scan status...")
    status = "running"
    while status in ["queued", "running"]:
        try:
            resp = requests.get(f"{BASE_URL}/scan/status/{scan_id}")
            resp.raise_for_status()
            status = resp.json()["status"]
            print(f"   Current Status: {status}")
            if status == "completed":
                break
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error polling status: {e}")
            return

    # 3. Get Report
    print("📋 Fetching final report...")
    try:
        resp = requests.get(f"{BASE_URL}/scan/report/{scan_id}")
        resp.raise_for_status()
        report = resp.json()
        print(f"✅ Report received. Found {len(report['vulnerabilities'])} vulnerabilities.")
        print(f"✅ Found {len(report['attack_paths'])} attack paths.")
    except Exception as e:
        print(f"❌ Failed to fetch report: {e}")
        return

    # 4. Test RAG Chat
    query = "What are the primary risks for this target and how do I mitigate them?"
    print(f"🤖 Sending query to Neural Core: '{query}'")
    try:
        resp = requests.post(f"{BASE_URL}/chat/query", json={"query": query, "scan_id": scan_id})
        resp.raise_for_status()
        ai_resp = resp.json()
        print("\n--- Neural Core Response ---")
        print(f"Summary: {ai_resp['Summary']}")
        print(f"Mitigation: {ai_resp['Mitigation']}")
        print("----------------------------\n")
        print("🎉 E2E Test Completed Successfully!")
    except Exception as e:
        print(f"❌ Chat query failed: {e}")

if __name__ == "__main__":
    test_full_flow()
