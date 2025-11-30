"""Data handling utilities for loading and saving user data."""
import json
import os
from pathlib import Path
from typing import Dict, Any


DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "user_data.json"


def load_data() -> Dict[str, Any]:
    """Load user data from JSON file. Returns empty structure if file doesn't exist."""
    if not DATA_FILE.exists():
        return {
            "personal_info": {
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "portfolio": ""
            },
            "job_experience": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "interests_and_background": []
        }
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate the structure
    if not validate_data(data):
        raise ValueError("Invalid data structure in user_data.json")
    
    return data


def save_data(data: Dict[str, Any]) -> None:
    """Save user data to JSON file."""
    # Validate before saving
    if not validate_data(data):
        raise ValueError("Invalid data structure - cannot save")
    
    DATA_DIR.mkdir(exist_ok=True)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Data saved to {DATA_FILE}")


def validate_data(data: Dict[str, Any]) -> bool:
    """
    Validate the structure of user data.
    
    Args:
        data: Dictionary containing user data
        
    Returns:
        True if data structure is valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    # Check required top-level keys
    required_keys = ['personal_info', 'job_experience']
    if not all(key in data for key in required_keys):
        return False
    
    # Validate personal_info structure
    personal_info = data.get('personal_info', {})
    if not isinstance(personal_info, dict):
        return False
    
    required_personal_fields = ['name', 'email', 'phone', 'location']
    if not all(field in personal_info for field in required_personal_fields):
        return False
    
    # Validate job_experience structure
    job_experience = data.get('job_experience', [])
    if not isinstance(job_experience, list):
        return False
    
    for job in job_experience:
        if not isinstance(job, dict):
            return False
        
        required_job_fields = ['title', 'company', 'position', 'start_date', 'end_date', 'duties']
        if not all(field in job for field in required_job_fields):
            return False
        
        if not isinstance(job.get('duties'), list):
            return False
    
    return True
