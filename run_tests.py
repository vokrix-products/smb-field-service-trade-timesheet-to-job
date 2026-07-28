import unittest
from unittest.mock import patch
from processor import process_file, THRESHOLD

class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.fake_extract = {
            "employee_name": "Jane Smith",
            "date": "2025-04-10",
            "hours_worked": 10.0,
            "hourly_rate": 50.0,
            "job_code": "ELEC-101",
            "job_estimated_cost": 480.0
        }

    @patch('processor.extract_timesheet_data')
    def test_process_file_above_threshold(self, mock_extract):
        self.fake_extract["hours_worked"] = 11.0  # actual = 550, variance = 70, pct = 0.1458 > threshold
        mock_extract.return_value = self.fake_extract
        records = process_file(b"dummy")
        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec["title"], "Jane Smith")
        self.assertEqual(rec["status"], "above_threshold:critical")
        self.assertAlmostEqual(rec["details"]["percentage_variance"], 70/480)

    @patch('processor.extract_timesheet_data')
    def test_process_file_within_threshold(self, mock_extract):
        mock_extract.return_value = self.fake_extract  # actual=500, pct=20/480=0.0417 <=0.1
        records = process_file(b"dummy")
        self.assertEqual(records[0]["status"], "within_threshold:good")

    @patch('processor.extract_timesheet_data')
    def test_missing_fields(self, mock_extract):
        mock_extract.return_value = {
            "employee_name": "Bob",
            "date": None,
            "hours_worked": None,
            "hourly_rate": None,
            "job_code": None,
            "job_estimated_cost": None
        }
        records = process_file(b"dummy")
        self.assertEqual(records[0]["status"], "within_threshold:good")
        self.assertIsNone(records[0]["details"]["actual_cost"])

    def test_threshold_constant(self):
        self.assertEqual(THRESHOLD, 0.10)

if __name__ == '__main__':
    unittest.main()
