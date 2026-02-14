import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def normalize_results(results: List[Dict]) -> List[Dict]:
    """Deduplicates and normalizes scan results."""
    unique_vulns = {}
    
    for vuln in results:
        # Create a unique key based on target, CVE and component
        key = f"{vuln['target']}_{vuln['cve_id']}_{vuln['component']}"
        
        if key not in unique_vulns:
            unique_vulns[key] = vuln
        else:
            # Keep the one with higher severity/CVSS if duplicate
            if vuln.get('cvss', 0) > unique_vulns[key].get('cvss', 0):
                unique_vulns[key] = vuln
                
    return list(unique_vulns.values())
