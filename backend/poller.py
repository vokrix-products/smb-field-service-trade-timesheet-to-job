import os
import time
import requests
from processor import process

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ["PRODUCT_ID"]
API_KEY = os.environ["ANTHROPIC_API_KEY"]

HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
}

def poll_jobs():
    url = f"{SUPABASE_URL}/rest/v1/jobs"
    params = {
        "select": "*",
        "status": "eq.pending",
        "job_type": "eq.process_upload",
        "product_id": f"eq.{PRODUCT_ID}",
        "order": "created_at.asc",
        "limit": "1",
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200 or not resp.json():
        return None
    return resp.json()[0]

def download_file(bucket: str, path: str) -> bytes:
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.content

def upload_result(bucket: str, path: str, data: bytes):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    resp = requests.post(url, headers=HEADERS, data=data)
    resp.raise_for_status()

def update_job(job_id: str, status: str, output_file_path=None, result_summary=None):
    url = f"{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}"
    payload = {
        "status": status,
        "completed_at": "now()",
    }
    if output_file_path:
        payload["output_file_path"] = output_file_path
    if result_summary:
        payload["result_summary"] = result_summary
    resp = requests.patch(url, headers=HEADERS, json=payload)
    resp.raise_for_status()

def main():
    while True:
        job = poll_jobs()
        if job:
            job_id = job["id"]
            try:
                # Download input file
                file_content = download_file("uploads", job["source_file_path"])
                # Process with AI
                output = process(file_content, job)  # processor must accept bytes and job dict
                # Upload result
                result_path = f"results/{job_id}/output.json"
                upload_result("results", result_path, output.encode())
                # Update job as completed
                update_job(job_id, "completed", output_file_path=result_path, result_summary="Processed")
            except Exception as e:
                update_job(job_id, "failed", result_summary=str(e))
        time.sleep(60)

if __name__ == "__main__":
    main()
