import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class NiktoAdapter:
    def __init__(self):
        self.tool_name = "nikto"

    def is_available(self):
        try:
            subprocess.run(["nikto", "-Version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_scan(self, target: str):
        if not self.is_available():
            logger.warning(f"Scan aborted: Nikto tool not found on system for target {target}")
            return []

        try:
            cmd = ["nikto", "-h", target, "-Format", "csv", "-o", "-", "-Tuning", "1,2,3", "-timeout", "5"]
            logger.info(f"Starting Nikto scan for {target}")
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if not result.stdout.strip() and result.stderr:
                logger.error(f"Nikto produced no output, but stderr has errors: {result.stderr}")

            logger.info(f"Nikto scan completed for {target}")
            return self.parse_results(result.stdout, target)
        except subprocess.TimeoutExpired:
            logger.warning(f"Nikto scan timed out for {target}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during Nikto scan for {target}: {str(e)}")
            return []

    def parse_results(self, output: str, target: str):
        import csv
        import io
        vulns = []
        try:
            logger.debug(f"Parsing Nikto CSV output for {target}")
            f = io.StringIO(output)
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 7: continue
                if "Nikto" in row[0] or row[0].startswith("----------------"): continue
                
                vulns.append({
                    "target": target,
                    "cve_id": "N/A",
                    "severity": "Medium",
                    "cvss": 5.0,
                    "description": row[6],
                    "component": "web-server",
                    "evidence": row[5],
                    "source_tool": "nikto"
                })
            logger.info(f"Nikto parsing finished: Found {len(vulns)} vulnerabilities for {target}")
            return vulns
        except Exception as e:
            logger.error(f"Failed to parse Nikto CSV for {target}: {str(e)}")
            return []
