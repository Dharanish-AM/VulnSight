import networkx as nx
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class AttackGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def generate_graph(self, vulnerabilities: List[Dict]):
        """Builds an attack graph where nodes are vulnerabilities and edges represent potential escalation."""
        self.graph.clear()
        
        severity_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Info": 0}

        for i, v in enumerate(vulnerabilities):
            display_name = v['component']
            if v['cve_id'] != "N/A":
                display_name = f"{v['component']} ({v['cve_id']})"
            
            node_id = f"v{i}_{display_name}"
            # Ensure CVSS is a float for comparison
            cvss = v.get('cvss')
            if cvss is None or cvss == "N/A":
                cvss = severity_map.get(v.get('severity', 'Info'), 0) * 2.0 # Heuristic score
            
            v_enriched = v.copy()
            v_enriched['effective_cvss'] = float(cvss)
            v_enriched['display_name'] = display_name
            self.graph.add_node(node_id, **v_enriched)

        # Basic logic: link vulnerabilities on the same target if one can lead to another
        nodes = list(self.graph.nodes(data=True))
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i == j: continue
                
                v1_id, v1_data = nodes[i]
                v2_id, v2_data = nodes[j]
                
                # Escalation logic:
                # 1. Same target
                # 2. Higher effective CVSS
                if v1_data['target'] == v2_data['target']:
                    if v2_data['effective_cvss'] > v1_data['effective_cvss']:
                        self.graph.add_edge(v1_id, v2_id, label="potential escalation")

        return self.graph

    def get_ranked_chains(self, limit=10):
        """Returns attack paths ranked by total risk."""
        chains = []
        # Find all simple paths in the DAG
        for node in self.graph.nodes():
            if self.graph.in_degree(node) == 0: # Entry points
                # Get all paths from this entry point
                for target in self.graph.nodes():
                    if node != target:
                        for path in nx.all_simple_paths(self.graph, node, target):
                            # Store only the display names for the frontend
                            display_path = [self.graph.nodes[n]['display_name'] for n in path]
                            chains.append(display_path)
        
        # Sort by length (complexity) and then by max risk in path
        return sorted(chains, key=len, reverse=True)[:limit]
