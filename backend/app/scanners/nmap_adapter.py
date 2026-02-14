import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class NmapAdapter:
    def __init__(self):
        self.tool_name = "nmap"

    def is_available(self):
        try:
            subprocess.run(["nmap", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_scan(self, target: str):
        if not self.is_available():
            logger.warning(f"Scan aborted: Nmap tool not found on system for target {target}")
            return []

        try:
            cmd = ["nmap", "-F", "-sV", "--script", "vulners", "-oX", "-", target]
            logger.info(f"Starting Nmap scan for {target}")
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Nmap scan completed for {target}")
            return self.parse_results(result.stdout, target)
        except subprocess.CalledProcessError as e:
            logger.error(f"Nmap process failed for {target}: {e.stderr}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during Nmap scan for {target}: {str(e)}")
            return []

    def parse_results(self, xml_output: str, target: str):
        import xml.etree.ElementTree as ET
        vulns = []
        try:
            logger.debug(f"Parsing Nmap XML output for {target}")
            root = ET.fromstring(xml_output)
            for host in root.findall('host'):
                for port in host.find('ports').findall('port'):
                    service = port.find('service')
                    if service is not None:
                        script = port.find('.//script[@id="vulners"]')
                        if script is not None:
                            output_text = script.get('output', '')
                            lines = output_text.splitlines()
                            for line in lines:
                                if 'CVE-' in line:
                                    parts = line.split()
                                    cve_id = next((p for p in parts if p.startswith('CVE-')), "N/A")
                                    vulns.append({
                                        "target": target,
                                        "cve_id": cve_id,
                                        "severity": "Medium",
                                        "cvss": 5.0,
                                        "description": f"Found via nmap vulners script: {line.strip()}",
                                        "component": service.get('name', 'unknown'),
                                        "evidence": f"Port {port.get('portid')} open",
                                        "source_tool": "nmap"
                                    })
            logger.info(f"Nmap parsing finished: Found {len(vulns)} vulnerabilities for {target}")
            return vulns
        except Exception as e:
            logger.error(f"Failed to parse Nmap XML for {target}: {str(e)}")
            return []
