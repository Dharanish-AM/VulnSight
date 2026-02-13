import nmap
import json
import os
from datetime import datetime
from logger import get_logger

logger = get_logger("Scanner")

import time

class VulnScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def scan(self, target: str):
        start_time = time.time()
        try:
            # Phase 1: Rapid Discovery (-F for top 100 ports, -T5 for insane speed)
            logger.info(f"Phase 1: Lightning-fast port discovery for {target}...")
            self.nm.scan(target, arguments='-F -T5')
            
            hosts = self.nm.all_hosts()
            if not hosts:
                logger.warning(f"No response from {target} during Phase 1 discovery.")
                return {"error": "Host unreachable or blocking probes"}

            found_host = hosts[0]
            open_ports = [port for port, info in self.nm[found_host].get('tcp', {}).items() if info['state'] == 'open']
            
            if not open_ports:
                logger.info(f"No open ports found on {target}. Skipping Phase 2.")
                return self.nm[found_host]

            # Phase 2: Targeted Probing (Only on identified open ports)
            ports_str = ",".join(map(str, open_ports))
            logger.info(f"Phase 2: Targeted vulnerability scan for {target} on ports: {ports_str}")
            
            args = '-sV -T4 --script "vuln and not (brute or broadcast or dos)" --min-parallelism 10'
            self.nm.scan(target, ports=ports_str, arguments=args)
            
            # Robust retrieval: Nmap might label the host by IP or a different hostname
            if target in self.nm.all_hosts():
                scan_data = self.nm[target]
            elif self.nm.all_hosts():
                scan_data = self.nm[self.nm.all_hosts()[0]]
            else:
                raise Exception(f"No results found for {target} after Phase 2")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_file = f"data/raw_scan_{timestamp}.json"
            os.makedirs("data", exist_ok=True)
            with open(raw_file, "w") as f:
                json.dump(scan_data, f, indent=4)
                
            duration = time.time() - start_time
            logger.info(f"Ultra-fast scan for {target} completed in {duration:.2f} seconds.")
            return scan_data
        except Exception as e:
            # Handle potential byte-string errors from Nmap subprocess
            if isinstance(e, bytes):
                error_msg = e.decode('utf-8', errors='ignore')
            else:
                error_msg = str(e)
                
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "... [truncated]"
            logger.error(f"Error during nmap scan: {error_msg}")
            return {"error": error_msg}

if __name__ == "__main__":
    scanner = VulnScanner()
    # Test scan on scanme.nmap.org
    result = scanner.scan("scanme.nmap.org")
    print(json.dumps(result, indent=2))
