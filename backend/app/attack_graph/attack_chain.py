import networkx as nx
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class AttackGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.categories = {
            "INFO_GATHERING": ["waf-detect", "dns-waf-detect", "tech-detect", "rdap-whois", "spf-record-detect", "caa-fingerprint", "txt-fingerprint", "nameserver-fingerprint", "mx-fingerprint", "aaaa-fingerprint"],
            "RECON": ["ssl-issuer", "ssl-dns-names", "wildcard-tls", "azure-domain-tenant"],
            "CONFIGURATION": ["http-missing-security-headers", "deprecated-tls", "tls-version", "weak-cipher-suites"],
            "VULNERABILITY": ["web-server"],
            "EXPLOITATION": []
        }

    def _get_category(self, component: str) -> str:
        for cat, components in self.categories.items():
            if component in components:
                return cat
        return "UNKNOWN"

    def generate_graph(self, vulnerabilities: List[Dict]):
        self.graph.clear()
        
        severity_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Info": 0}
        category_order = ["INFO_GATHERING", "RECON", "CONFIGURATION", "VULNERABILITY", "EXPLOITATION"]

        for i, v in enumerate(vulnerabilities):
            display_name = v['component']
            if v['cve_id'] != "N/A":
                display_name = f"{v['component']} ({v['cve_id']})"
            
            node_id = f"v{i}_{display_name}"
            cvss = v.get('cvss')
            if cvss is None or cvss == "N/A":
                cvss = severity_map.get(v.get('severity', 'Info'), 0) * 2.0
            
            v_enriched = v.copy()
            v_enriched['effective_cvss'] = float(cvss)
            v_enriched['display_name'] = display_name
            v_enriched['category'] = self._get_category(v['component'])
            self.graph.add_node(node_id, **v_enriched)

        nodes = list(self.graph.nodes(data=True))
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i == j: continue
                
                v1_id, v1_data = nodes[i]
                v2_id, v2_data = nodes[j]
                
                if v1_data['target'] != v2_data['target']: continue

                cat1 = v1_data['category']
                cat2 = v2_data['category']

                try:
                    idx1 = category_order.index(cat1)
                    idx2 = category_order.index(cat2)

                    # Logical Flow: 
                    # 1. Info Gathering -> Recon
                    # 2. Recon -> Configuration
                    # 3. Configuration -> Vulnerability
                    # 4. Or direct jumps if severity increases significantly
                    if idx2 == idx1 + 1:
                        self.graph.add_edge(v1_id, v2_id, label="logical progression")
                    elif idx2 > idx1 and v2_data['effective_cvss'] > v1_data['effective_cvss']:
                        self.graph.add_edge(v1_id, v2_id, label="escalation")
                except ValueError:
                    continue

        return self.graph

    def get_ranked_chains(self, limit=10):
        chains = []
        for node in self.graph.nodes():
            if self.graph.in_degree(node) == 0:
                for target in self.graph.nodes():
                    if node != target and self.graph.out_degree(target) == 0:
                        for path in nx.all_simple_paths(self.graph, node, target):
                            display_path = [self.graph.nodes[n]['display_name'] for n in path]
                            if len(display_path) > 1:
                                chains.append(display_path)
        
        return sorted(chains, key=lambda x: (len(x), self.graph.nodes[f"v0_{x[-1]}"]['effective_cvss'] if f"v0_{x[-1]}" in self.graph else 0), reverse=True)[:limit]
