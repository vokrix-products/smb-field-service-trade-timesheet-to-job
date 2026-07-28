import os
import json
from openai import OpenAI

THRESHOLD = 0.10  # 10% variance threshold

def extract_timesheet_data(text: str) -> dict:
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    system_prompt = (
        "You are an assistant that extracts structured data from timesheet text. "
        "Extract exactly the following fields: employee_name, date (YYYY-MM-DD), hours_worked (float), "
        "hourly_rate (float), job_code, job_estimated_cost (float). "
        "Always return a JSON object with those keys. If any field is missing, use null."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    data = json.loads(content)
    return data

def process_file(file_bytes: bytes) -> list[dict]:
    try:
        text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return []
    
    extracted = extract_timesheet_data(text)
    
    employee_name = extracted.get("employee_name", "Unknown")
    date_str = extracted.get("date")
    hours = extracted.get("hours_worked")
    rate = extracted.get("hourly_rate")
    job_estimated_cost = extracted.get("job_estimated_cost")
    
    actual_cost = None
    variance = None
    pct_variance = None
    if hours is not None and rate is not None:
        actual_cost = hours * rate
    if actual_cost is not None and job_estimated_cost is not None and job_estimated_cost != 0:
        variance = actual_cost - job_estimated_cost
        pct_variance = abs(variance) / abs(job_estimated_cost)
    
    status = "within_threshold:good"
    if pct_variance is not None and pct_variance > THRESHOLD:
        status = "above_threshold:critical"
    
    details = {
        "employee_name": employee_name,
        "date": date_str,
        "hours_worked": hours,
        "hourly_rate": rate,
        "job_code": extracted.get("job_code"),
        "job_estimated_cost": job_estimated_cost,
        "actual_cost": actual_cost,
        "variance": variance,
        "percentage_variance": pct_variance
    }
    due_date = date_str  # ISO date string, may be None
    
    record = {
        "title": employee_name,
        "status": status,
        "details": details,
        "due_date": due_date
    }
    return [record]
