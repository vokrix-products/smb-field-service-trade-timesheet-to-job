# SMB Field Service Timesheet-to-Job-Cost Variance Auto-Processor

Processes timesheet text files to extract labour details, compare actual cost against estimated job cost, and flag variances.

## Product Archetype
Backend microservice for SMB field service / trade companies. Automates timesheet-to-job-cost variance analysis using AI (DeepSeek Chat). Deployed as a continuous poller that reads uploads from Supabase storage, processes them, and writes variance records to Supabase tables.

## Input Format
Expects plain text timesheets with fields: Employee Name, Date (YYYY-MM-DD), Hours Worked, Hourly Rate, Job Code, Job Estimated Cost. Example:
```
Employee Name: John Doe
Date: 2025-04-08
Hours Worked: 8.5
Hourly Rate: 35.00
Job Code: ROOF-042
Job Estimated Cost: 300.00
```

## How It Works
- **poller.py** monitors Supabase `jobs` table for `pending` jobs of type `process_upload`.
- Downloads the uploaded file from Supabase Storage.
- **processor.py** calls DeepSeek Chat to extract structured fields, computes actual cost (hours × rate), compares to estimated cost, and assigns a status based on a 10% variance threshold.
- Writes resulting records to Supabase `records` table.
- Updates job status to `completed` or `failed`.

## Deploy on Railway
1. Create Railway project from this repo.
2. Set environment variables:
   - `DEEPSEEK_API_KEY` (your DeepSeek API key)
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `PRODUCT_ID`
3. Deploy the poller: `python poller.py`

## Testing Offline
```bash
python run_demo.py    # hardcoded sample, prints one record
python run_tests.py   # unit tests (mock API, no key needed)
```

## Threshold
Variance threshold: **10%** (0.10). Statuses:
- `within_threshold:good` – variance ≤ 10%
- `above_threshold:critical` – variance > 10%

Dashboard: https://smb-field-service-trade-timesheet-to-job.vokrix.co, Vercel: smb-field-service-trade-timesheet-to-job, Railway: d02cca25-be59-4fad-a0ef-97aa2093cccd
Railway: smb-field-service-trade-timesheet-to-job
Cloudflare: smb-field-service-trade-timesheet-to-job.vokrix.co

Billing: price_1TyDZU2c9uGCcgMSQNeSYlBz
