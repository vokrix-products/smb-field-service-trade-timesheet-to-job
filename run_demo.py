import json
from processor import process_file

def main():
    sample_text = (
        "Employee Name: John Doe\n"
        "Date: 2025-04-08\n"
        "Hours Worked: 8.5\n"
        "Hourly Rate: 35.00\n"
        "Job Code: ROOF-042\n"
        "Job Estimated Cost: 300.00\n"
    )
    data_bytes = sample_text.encode('utf-8')
    records = process_file(data_bytes)
    print("Processed records:")
    print(json.dumps(records, indent=2))

if __name__ == "__main__":
    main()
