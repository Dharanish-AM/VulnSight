from urllib.parse import urlparse
import re

def normalize_target(target: str) -> dict:
    """
    Parses a target string and returns different formats needed by scanners.
    """
    # Remove protocol if present
    parsed = urlparse(target)
    
    # If no protocol (e.g. google.com), urlparse might put the whole thing in 'path'
    if not parsed.scheme:
        # Check if it has a port or is just a hostname
        host = target.split('/')[0].split(':')[0]
        url = f"http://{target.rstrip('/')}"
    else:
        host = parsed.netloc.split(':')[0]
        url = target.rstrip('/')

    return {
        "host": host,
        "url": url,
        "original": target
    }

def is_valid_ip(target: str) -> bool:
    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return bool(ip_pattern.match(target))
