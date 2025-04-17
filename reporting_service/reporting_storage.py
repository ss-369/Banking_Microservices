import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportStorage:
    """Storage handler for reporting service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        self.data_dir = data_dir
        self.reports_file = f"{data_dir}/reports.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Create reports file if it doesn't exist
        if not os.path.exists(self.reports_file):
            with open(self.reports_file, 'w') as f:
                json.dump([], f)
    
    def get_all_reports(self):
        """Get all reports from storage"""
        try:
            with open(self.reports_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading reports file: {e}")
            return []
    
    def get_report(self, report_id):
        """Get report by ID"""
        reports = self.get_all_reports()
        
        for report in reports:
            if report['id'] == report_id:
                return report
        
        return None
    
    def get_reports_by_user_id(self, user_id):
        """Get all reports for a specific user"""
        reports = self.get_all_reports()
        
        # Filter reports by user_id
        user_reports = [report for report in reports if report.get('parameters', {}).get('user_id') == user_id]
        
        return user_reports
    
    def save_report(self, report_data):
        """Save a report"""
        reports = self.get_all_reports()
        
        # Check if report with this ID already exists
        for i, report in enumerate(reports):
            if report['id'] == report_data['id']:
                reports[i] = report_data
                break
        else:
            reports.append(report_data)
        
        try:
            with open(self.reports_file, 'w') as f:
                json.dump(reports, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error writing report data: {e}")
            return False
    
    def delete_report(self, report_id):
        """Delete a report"""
        reports = self.get_all_reports()
        
        for i, report in enumerate(reports):
            if report['id'] == report_id:
                reports.pop(i)
                
                try:
                    with open(self.reports_file, 'w') as f:
                        json.dump(reports, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Error deleting report data: {e}")
                    return False
        
        return False
