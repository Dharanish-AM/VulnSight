import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class NucleiAdapter:
    def __init__(self):
        self.tool_name = "nuclei"

    def is_available(self):
        try:
            subprocess.run(["nuclei", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_scan(self, target: str):
        if not self.is_available():
            logger.warning(f"Scan aborted: Nuclei tool not found on system for target {target}")
            return []

        try:
            cmd = ["nuclei", "-u", target, "-silent", "-j", "-c", "50"]
            logger.info(f"Starting Nuclei scan for {target}")
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            logger.info(f"Nuclei scan completed for {target}")
            return self.parse_results(result.stdout, target)
        except Exception as e:
            logger.error(f"Unexpected error during Nuclei scan for {target}: {str(e)}")
            return []

    def parse_results(self, output: str, target: str):
        vulns = []
        logger.debug(f"Parsing Nuclei JSON output for {target}")
        for line in output.splitlines():
            try:
                data = json.loads(line)
                info = data.get("info", {})
                classification = info.get("classification", {})
                vulns.append({
                    "target": target,
                    "cve_id": classification.get("cve-id") or "N/A",
                    "severity": info.get("severity", "Info").capitalize(),
                    "cvss": classification.get("cvss-score") or 0.0,
                    "description": info.get("description") or "No description",
                    "component": data.get("template-id", "unknown"),
                    "evidence": data.get("matched-at") or "N/A",
                    "source_tool": "nuclei"
                })
            except:
                continue
        logger.info(f"Nuclei parsing finished: Found {len(vulns)} vulnerabilities for {target}")
        return vulns
