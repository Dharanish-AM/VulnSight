import httpx
import asyncio
import json
import time
import sys

BASE_URL = "http://localhost:8000"

async def test_health():
    print("\n[1/4] Checking API Health...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/results")
            if response.status_code == 200:
                print("  ✅ Backend is reachable.")
                return True
            else:
                print(f"  ❌ Backend returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"  ❌ Failed to connect: {type(e).__name__}: {e}")
        return False

async def test_scan():
    print("\n[2/4] Testing Ultra-Fast Scan (Target: 1.1.1.1)...")
    print("  (Phase 1: Discovery -> Phase 2: Targeted scripts)")
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            start = time.time()
            response = await client.post(
                f"{BASE_URL}/scan",
                json={"target": "1.1.1.1"},
                headers={"Content-Type": "application/json"}
            )
            duration = time.time() - start
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Scan completed in {duration:.2f}s")
                results_count = len(data.get('results', []))
                print(f"  ✅ Data collected for {results_count} service(s).")
                return True
            else:
                print(f"  ❌ Scan failed ({response.status_code}): {response.text}")
                return False
    except Exception as e:
        print(f"  ❌ Scan error: {type(e).__name__}: {str(e)}")
        return False

async def test_results():
    print("\n[3/4] Testing Results Retrieval...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/results")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Retrieved {len(data.get('results', []))} results from storage.")
                return True
            else:
                print(f"  ❌ Results failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"  ❌ Results error: {e}")
        return False

async def test_ai():
    print("\n[4/4] Testing AI Insight Integration...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Check if there's actual results to analyze
            res = await client.get(f"{BASE_URL}/results")
            if res.status_code == 200 and not res.json().get("results"):
                print("  ⚠️ Skipping AI test: No open ports found to analyze.")
                return True

            response = await client.post(
                f"{BASE_URL}/chat",
                json={"question": "What is the most critical port found?", "scan_id": "latest"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ AI Response: {data.get('response', '')[:100]}...")
                return True
            else:
                print(f"  ❌ AI Chat failed ({response.status_code}): {response.text}")
                return False
    except Exception as e:
        print(f"  ❌ AI error: {type(e).__name__}: {str(e)}")
        return False

async def run_all_tests():
    print("="*45)
    print("      VulnSight Backend Verification Suite")
    print("="*45)
    
    if not await test_health():
        print("\n🛑 ERROR: Backend is not running on http://localhost:8000")
        print("Please run 'uvicorn main:app --reload' in the backend folder first.")
        sys.exit(1)
        
    results = {
        "Scan": await test_scan(),
        "Results": await test_results(),
        "AI": await test_ai()
    }
    
    print("\n" + "="*45)
    print("Final Status Report:")
    for test, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {test:10}: {status}")
    print("="*45)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
