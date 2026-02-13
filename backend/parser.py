import os
from logger import get_logger

logger = get_logger("Parser")

class ScanParser:
    def parse(self, scan_data: dict):
        results = []
        
        # The scan_data structure from python-nmap depends on findings
        # Usually it's scan_data['tcp'] or scan_data['udp']
        
        if 'tcp' not in scan_data:
            return {"vulnerabilities": []}

        for port, info in scan_data['tcp'].items():
            service = info.get('name', 'unknown')
            version = info.get('version', '')
            product = info.get('product', '')
            
            # Extract script outputs (where vulnerabilities are listed)
            script_output = info.get('script', {})
            
            vulns = []
            if script_output:
                for script_id, output in script_output.items():
                    if 'vuln' in script_id or 'vuln' in output.lower():
                        # Basic parsing of vulnerability info
                        # In a real app, this would be more sophisticated
                        vulns.append({
                            "id": script_id,
                            "output": output
                        })

            results.append({
                "port": port,
                "service": f"{product} {service} {version}".strip(),
                "vulnerabilities": vulns
            })

        target = scan_data.get('hostnames', [{}])[0].get('name', 'unknown')
        logger.info(f"Parsing scan results for {target}. Found {len(results)} ports.")
        
        return {
            "target": target,
            "results": results
        }

if __name__ == "__main__":
    # Test with a dummy file if exists or mock data
    parser = ScanParser()
    # Mock data for testing
    mock_data = {
        "hostnames": [{"name": "example.com"}],
        "tcp": {
            "80": {
                "name": "http",
                "product": "Apache",
                "version": "2.4.41",
                "script": {
                    "http-vuln-cve2017-5638": "Vulnerable: Yes\nCVE-2017-5638"
                }
            }
        }
    }
    print(json.dumps(parser.parse(mock_data), indent=2))
