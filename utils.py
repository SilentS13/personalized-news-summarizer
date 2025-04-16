import re
from urllib.parse import urlparse

def is_valid_url(url):
    """Check if the input is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_valid_email(email):
    """Check if the email is valid."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def truncate_text(text, max_length=200):
    """Truncate text to a certain length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

def get_reading_level_options():
    """Return reading level options for the UI."""
    return [
        {"value": "basic", "label": "Basic - Simpler language and shorter sentences"},
        {"value": "medium", "label": "Medium - Balanced complexity"},
        {"value": "advanced", "label": "Advanced - Maintain original complexity"}
    ]

def get_summary_length_options():
    """Return summary length options for the UI."""
    return [
        {"value": "brief", "label": "Brief - Concise overview"},
        {"value": "medium", "label": "Medium - Balanced summary"},
        {"value": "detailed", "label": "Detailed - Comprehensive summary"}
    ]

def get_interest_categories():
    """Return common interest categories for the UI."""
    return [
        "Politics", "Business", "Technology", "Science", "Health", 
        "Sports", "Entertainment", "World News", "Environment", 
        "Education", "Arts", "Travel", "Food", "Fashion", "Lifestyle"
    ]

def format_date(date):
    """Format a datetime object to a readable string."""
    return date.strftime("%B %d, %Y %H:%M")