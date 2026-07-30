import os, time, json
import requests
from processor import process_file

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ["PRODUCT_ID"]
HEADERS = {"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json"}

def poll_jobs():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/jobs", headers=HEADERS,
        params={"select": "*", "status": "eq.pending", "job_type": "eq.process_upload", "product_id": f"eq.{PRODUCT_ID}"})
    r.raise_for_status()
    return r.json()

def download_file(path):
    r = requests.get(f"{SUPABASE_URL}/storage/v1/object/uploads/{path}", headers={"apikey": SUPABASE_SERVICE_KEY})
    r.raise_for_status()
    return r.content

def write_records(rows, customer_id, source_path):
    for row in rows:
        _r = requests.post(f"{SUPABASE_URL}/rest/v1/records", headers=HEADERS, json={
            "product_id": PRODUCT_ID, "customer_id": customer_id,
            "title": row.get("title", "Unknown"), "status": row.get("status", "pending"),
            "details": row.get("details", {}), "source_file_path": source_path,
            "due_date": row.get("due_date")
        })
        if not _r.ok:
            raise Exception(f"records 400: {_r.text[:300]}")
        _r.raise_for_status()

def update_job(job_id, status, result_summary=None):
    payload = {"status": status}
    if result_summary: payload["result_summary"] = result_summary
    requests.patch(f"{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}", headers=HEADERS, json=payload).raise_for_status()

def main():
    print("Poller started", flush=True)
    while True:
        try:
            for job in poll_jobs():
                job_id, customer_id = job["id"], job.get("customer_id")
                paths = job.get("input_file_paths") or ([job["input_file_path"]] if job.get("input_file_path") else [])
                if not paths:
                    update_job(job_id, "failed", "No input files")
                    continue
                update_job(job_id, "processing")
                try:
                    total = 0
                    for path in paths:
                        rows = process_file(download_file(path))
                        write_records(rows, customer_id, path)
                        total += len(rows)
                    update_job(job_id, "completed", json.dumps({"total": total}))
                except Exception as e:
                    update_job(job_id, "failed", str(e)[:200])
        except Exception as e:
            print(f"Poll error: {e}", flush=True)
        time.sleep(30)

if __name__ == "__main__":
    main()
