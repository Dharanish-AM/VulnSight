import requests
import logging

logger = logging.getLogger(__name__)

def enrich_vulnerability(cve_id: str):
    """Fetches details for a CVE from NVD or a mock source."""
    if cve_id == "N/A":
        return None

    try:
        # Try local enrichment first (Mock for MVP)
        mock_db = {
            "CVE-2023-1234": {
                "cvss": 7.5,
                "remediation": "Update to the latest version of the service.",
                "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-1234"]
            },
            "CVE-2022-22965": {
                "cvss": 9.8,
                "remediation": "Apply official Spring Framework patches.",
                "references": ["https://tanzu.vmware.com/security/cve-2022-22965"]
            }
        }
        
        return mock_db.get(cve_id, {
            "cvss": 5.0,
            "remediation": "Follow general security hardening best practices.",
            "references": []
        })
    except Exception as e:
        logger.error(f"Enrichment failed for {cve_id}: {e}")
        return None
