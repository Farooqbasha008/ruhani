from datetime import datetime, timedelta
from typing import Any, Dict

def generate_timestamp_ranges(days: int = 7) -> Dict[str, datetime]:
    """Generate timestamp ranges for analytics queries"""
    now = datetime.utcnow()
    return {
        "now": now,
        "start": now - timedelta(days=days),
        "yesterday": now - timedelta(days=1),
        "last_week": now - timedelta(days=7),
        "last_month": now - timedelta(days=30),
    }

def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Normalize scores to 0-1 range"""
    if not scores:
        return {}
    
    min_val = min(scores.values())
    max_val = max(scores.values())
    
    if min_val == max_val:
        return {k: 0.5 for k in scores.keys()}
    
    return {k: (v - min_val) / (max_val - min_val) for k, v in scores.items()}

def anonymize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove personally identifiable information from data"""
    if not data:
        return {}
    
    anonymized = data.copy()
    fields_to_remove = ["email", "name", "profile_picture", "department", "team"]
    
    for field in fields_to_remove:
        anonymized.pop(field, None)
    
    return anonymized