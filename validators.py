import re

def valid_code(value): return bool(re.fullmatch(r"[A-Za-z0-9_-]{2,60}",value or ""))
def valid_email(value): return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",value or ""))
def positive_number(value): return float(value)>0
