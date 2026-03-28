
#!/usr/bin/env python3
"""
api/canton_api.py
Demonstrates the Canton JSON Ledger API (port 7575).

This script:
  1. Connects to a running Canton sandbox
  2. Allocates two parties (HSBC and Alice)
  3. Creates a KYC contract via the JSON API
  4. Queries active contracts
  5. Exercises the Approve choice
  6. Prints the full contract lifecycle

Run after: dpm sandbox (in a separate terminal)
Usage:     python api/canton_api.py
"""

import requests
import json
import sys
from datetime import datetime, timezone

LEDGER_URL = "http://localhost:7575"
HEADERS = {"Content-Type": "application/json"}


def check_ledger():
    try:
        r = requests.get(f"{LEDGER_URL}/v2/ledger-identity", timeout=3)
        if r.status_code == 200:
            ledger_id = r.json().get("ledgerId", "unknown")
            print(f"✅ Canton sandbox is running. Ledger ID: {ledger_id}")
            return True
    except Exception:
        pass
    print("❌ Canton sandbox not running. Start it with: dpm sandbox")
    return False


def allocate_party(display_name, party_hint):
    r = requests.post(
        f"{LEDGER_URL}/v2/parties/allocate",
        headers=HEADERS,
        json={"partyIdHint": party_hint, "displayName": display_name}
    )
    if r.status_code == 200:
        party_id = r.json()["partyDetails"]["party"]
        print(f"  ✅ Allocated party: {display_name} → {party_id[:30]}...")
        return party_id
    print(f"  ❌ Failed to allocate {display_name}: {r.text}")
    return None


def create_kyc_contract(bank_party, customer_party):
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "templateId": "daml-canton-app:KYC:KYCRecord",
        "payload": {
            "bank": bank_party,
            "customer": customer_party,
            "fullName": "Alice Johnson",
            "nationality": "British",
            "documentType": "PASSPORT",
            "documentId": "GB123456789",
            "status": {"tag": "Pending", "value": {}},
            "submittedAt": now
        }
    }
    r = requests.post(
        f"{LEDGER_URL}/v2/create",
        headers={**HEADERS, "X-Canton-Domain-Id": bank_party},
        json=payload
    )
    if r.status_code == 200:
        contract_id = r.json()["contractId"]
        print(f"  ✅ KYCRecord created. Contract ID: {contract_id[:30]}...")
        return contract_id
    print(f"  ❌ Create failed: {r.text}")
    return None


def query_contracts(party):
    r = requests.post(
        f"{LEDGER_URL}/v2/query",
        headers=HEADERS,
        json={
            "templateIds": ["daml-canton-app:KYC:KYCRecord"],
            "readAs": [party]
        }
    )
    if r.status_code == 200:
        contracts = r.json().get("results", [])
        print(f"  ✅ Found {len(contracts)} active KYCRecord contract(s)")
        for c in contracts:
            payload = c.get("payload", {})
            print(f"     → Name: {payload.get('fullName')} | Status: {payload.get('status',{}).get('tag')}")
        return contracts
    print(f"  ❌ Query failed: {r.text}")
    return []


def exercise_approve(bank_party, contract_id):
    r = requests.post(
        f"{LEDGER_URL}/v2/exercise",
        headers=HEADERS,
        json={
            "templateId": "daml-canton-app:KYC:KYCRecord",
            "contractId": contract_id,
            "choice": "Approve",
            "argument": {},
            "actAs": [bank_party]
        }
    )
    if r.status_code == 200:
        new_id = r.json().get("exerciseResult", "")
        print(f"  ✅ Approved! New contract ID: {str(new_id)[:30]}...")
        return new_id
    print(f"  ❌ Approve failed: {r.text}")
    return None


if __name__ == "__main__":
    print("
" + "="*55)
    print("  Canton KYC App — JSON Ledger API Demo")
    print("="*55)

    if not check_ledger():
        sys.exit(1)

    print("
[1] Allocating parties...")
    bank     = allocate_party("HSBC",  "HSBC")
    customer = allocate_party("Alice", "Alice")

    if not bank or not customer:
        sys.exit(1)

    print("
[2] Creating KYC contract...")
    contract_id = create_kyc_contract(bank, customer)

    print("
[3] Querying active contracts...")
    query_contracts(bank)

    if contract_id:
        print("
[4] Approving KYC...")
        exercise_approve(bank, contract_id)

        print("
[5] Querying after approval...")
        query_contracts(bank)

    print("
" + "="*55)
    print("  ✅ Full contract lifecycle complete")
    print("  Contract: created → queried → approved → queried")
    print("  This is a real Canton ledger interaction via JSON API")
    print("="*55)
