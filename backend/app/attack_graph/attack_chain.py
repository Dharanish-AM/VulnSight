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
        
        for i, v in enumerate(vulnerabilities):
            node_id = f"v{i}_{v['cve_id']}"
            self.graph.add_node(node_id, **v)

        # Basic logic: link vulnerabilities on the same target if one can lead to another
        # e.g., Low severity vuln leading to a High severity one
        nodes = list(self.graph.nodes(data=True))
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i == j: continue
                
                v1_id, v1_data = nodes[i]
                v2_id, v2_data = nodes[j]
                
                if v1_data['target'] == v2_data['target']:
                    # Simple heuristic: Escalation from lower to higher CVSS
                    if v2_data['cvss'] > v1_data['cvss']:
                        self.graph.add_edge(v1_id, v2_id, label="potential escalation")

        return self.graph

    def get_ranked_chains(self):
        """Returns attack paths ranked by total risk."""
        chains = []
        # Find all paths between nodes in the DAG
        # This is a simple representation for the MVP
        for node in self.graph.nodes():
            if self.graph.in_degree(node) == 0: # Start nodes
                paths = nx.single_source_shortest_path(self.graph, node)
                for target, path in paths.items():
                    if len(path) > 1:
                        chains.append(path)
        
        return sorted(chains, key=len, reverse=True)
