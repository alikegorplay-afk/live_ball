import re

def clean_text(description):
    cleaned = re.sub(r'\s+', ' ', description)
    return cleaned.strip()