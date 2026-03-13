import subprocess
import logging
import json
import os

logger = logging.getLogger(__name__)

class SQLMapAdapter:
    def __init__(self):
        self.tool_name = "sqlmap"

    def is_available(self):
        try:
            subprocess.run(["sqlmap", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_scan(self, target: str):
        if not self.is_available():
            logger.warning(f"Scan aborted: SQLMap tool not found on system for target {target}")
            return []

        # For MVP, we run a non-intrusive scan
        try:
            # -u for URL, --batch for non-interactive, --random-agent to avoid blocks
            # We're just checking if it's vulnerable without deep exploitation
            cmd = ["sqlmap", "-u", target, "--batch", "--random-agent", "--level=1", "--risk=1"]
            logger.info(f"Starting SQLMap scan for {target}")
            
            # SQLMap output is mostly stdout text
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            logger.info(f"SQLMap scan completed for {target}")
            return self.parse_results(result.stdout, target)
        except Exception as e:
            logger.error(f"Error during SQLMap scan for {target}: {str(e)}")
            return []

    def parse_results(self, output: str, target: str):
        vulns = []
        # Look for injection points in the output
        if "is vulnerable" in output.lower() or "sql injection" in output.lower():
            vulns.append({
                "target": target,
                "cve_id": "CWE-89",
                "severity": "Critical",
                "cvss": 9.8,
                "description": "Potential SQL Injection vulnerability detected by SQLMap.",
                "component": "Web Application",
                "evidence": "Injected parameters found",
                "source_tool": "sqlmap"
            })
        
        logger.info(f"SQLMap parsing finished: Found {len(vulns)} vulnerabilities for {target}")
        return vulns
