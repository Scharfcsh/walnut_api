# import time
# import uuid
# import requests
# from datetime import datetime

# BASE_URL = "https://api.amslabs.in/v1"
# HEADERS = {"Content-Type": "application/json"}

# TXN_ID = f"processing_{uuid.uuid4().hex[:8]}_777"

# payload = {
#     "transaction_id": TXN_ID,
#     "source_account": "acc_proc_1",
#     "destination_account": "acc_proc_2",
#     "amount": 250.75,
#     "currency": "USD",
# }


# def log(msg):
#     ts = datetime.now().strftime("%H:%M:%S")
#     print(f"[{ts}] {msg}")


# def post_transaction():
#     log(f"🌐 POST {BASE_URL}/webhooks/transactions")
#     log(f"📤 Request JSON: {payload}")

#     start = time.time()
#     res = requests.post(
#         f"{BASE_URL}/webhooks/transactions",
#         json=payload,
#         headers=HEADERS,
#         timeout=5,
#     )
#     elapsed = (time.time() - start) * 1000

#     log(f"📥 {res.status_code} {BASE_URL}/webhooks/transactions")
#     log(f"📥 Body: {res.text}")
#     log(f"✅ Response Time: {elapsed:.1f}ms")

#     assert res.status_code == 202, "Expected 202 Accepted"
#     assert elapsed < 500, "Response took more than 500ms"


# def get_transaction():
#     log(f"🌐 GET {BASE_URL}/transactions/{TXN_ID}")
#     res = requests.get(
#         f"{BASE_URL}/transactions/{TXN_ID}",
#         headers=HEADERS,
#         timeout=5,
#     )
#     log(f"📥 {res.status_code} {BASE_URL}/transactions/{TXN_ID}")
#     log(f"📥 Body: {res.text}")
#     return res.json()


# def wait_for_processing(timeout=45, interval=3):
#     log("🧪 Testing transaction processing (will take ~35 seconds)...")
#     start = time.time()

#     while time.time() - start < timeout:
#         data = get_transaction()

#         # Not found is VALID early state
#         if (
#             isinstance(data, list)
#             and len(data) == 1
#             and data[0].get("message") == "Transaction not found"
#         ):
#             log("🕒 Transaction not yet persisted (acceptable)")
#             time.sleep(interval)
#             continue

#         txn = data[0]

#         if txn["status"] == "PROCESSING":
#             assert txn["processed_at"] is None
#             log("🕒 Status = PROCESSING")
#         elif txn["status"] == "PROCESSED":
#             assert txn["processed_at"] is not None
#             log("✅ Status = PROCESSED")
#             return
#         else:
#             raise AssertionError(f"Unexpected status {txn['status']}")

#         time.sleep(interval)

#     raise TimeoutError("❌ Transaction did not process within time")


# if __name__ == "__main__":
#     post_transaction()
#     # time.sleep(2)
#     wait_for_processing()



import time
import requests

BASE_URL = "https://api.amslabs.in"
TXN_ID = "processing_0fbead94_000000"

payload = {
    "amount": 250.75,
    "currency": "USD",
    "destination_account": "acc_proc_2",
    "source_account": "acc_proc_1",
    "transaction_id": TXN_ID,
}

headers = {"Content-Type": "application/json"}

print("🚀 Sending webhook...")
r = requests.post(f"{BASE_URL}/v1/webhooks/transactions", json=payload, headers=headers)
print("Webhook response:", r.status_code, r.text)

print("\n⚡ Immediately checking status...")
r = requests.get(f"{BASE_URL}/v1/transactions/{TXN_ID}")
print("Status response:", r.status_code, r.text)
