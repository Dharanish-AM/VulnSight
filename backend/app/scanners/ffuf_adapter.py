import subprocess
import logging
import json
import os

logger = logging.getLogger(__name__)

class FFUFAdapter:
    def __init__(self):
        self.tool_name = "ffuf"
        # Common wordlist locations on Unix systems
        self.wordlist_paths = [
            "/usr/share/wordlists/dirb/common.txt",
            "/usr/share/seclists/Discovery/Web-Content/common.txt",
            "tests/mock_wordlist.txt" # Fallback if we create one
        ]

    def is_available(self):
        try:
            subprocess.run(["ffuf", "-V"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_wordlist(self):
        for p in self.wordlist_paths:
            if os.path.exists(p):
                return p
        return None

    def run_scan(self, target: str):
        if not self.is_available():
            logger.warning(f"Scan aborted: FFUF tool not found on system for target {target}")
            return []

        wordlist = self.get_wordlist()
        if not wordlist:
            logger.warning(f"Scan aborted: No suitable wordlist found for FFUF on target {target}")
            return []

        try:
            # Ensure target URL ends with /FUZZ if it doesn't have it
            if "FUZZ" not in target:
                base_url = target.rstrip("/") + "/FUZZ"
            else:
                base_url = target

            # Output to a temp JSON file for easy parsing
            output_file = f"/tmp/ffuf_{os.getpid()}.json"
            cmd = ["ffuf", "-u", base_url, "-w", wordlist, "-o", output_file, "-of", "json", "-s"]
            
            logger.info(f"Starting FFUF scan for {target}")
            subprocess.run(cmd, capture_output=True, check=False) # ffuf might exit with non-zero if findings occur
            
            if not os.path.exists(output_file):
                return []

            with open(output_file, 'r') as f:
                data = json.load(f)
            
            os.remove(output_file)
            
            logger.info(f"FFUF scan completed for {target}")
            return self.parse_results(data, target)
        except Exception as e:
            logger.error(f"Error during FFUF scan for {target}: {str(e)}")
            return []

    def parse_results(self, data: dict, target: str):
        vulns = []
        results = data.get("results", [])
        
        # Filter for interesting findings (e.g., status 200 on sensitive paths)
        interesting_paths = [".env", "config.php", "admin/", ".git/", "wp-config.php"]
        
        for res in results:
            path = res.get("url", "")
            status = res.get("status", 0)
            
            if status == 200:
                is_sensitive = any(p in path for p in interesting_paths)
                vulns.append({
                    "target": target,
                    "cve_id": "CWE-200" if is_sensitive else "DISCOVERED-PATH",
                    "severity": "High" if is_sensitive else "Low",
                    "cvss": 7.5 if is_sensitive else 2.0,
                    "description": f"Exposed resource found via fuzzing: {path}",
                    "component": "Web Server",
                    "evidence": f"Status 200 at {path}",
                    "source_tool": "ffuf"
                })
        
        logger.info(f"FFUF parsing finished: Found {len(vulns)} vulnerabilities for {target}")
        return vulns
