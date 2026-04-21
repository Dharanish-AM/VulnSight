import networkx as nx
import logging
from collections import defaultdict
from urllib.parse import urlparse
from typing import List, Dict

logger = logging.getLogger(__name__)

class AttackGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.category_order = ["INFO_GATHERING", "RECON", "CONFIGURATION", "VULNERABILITY", "EXPLOITATION"]
        self.categories = {
            "INFO_GATHERING": [
                "waf-detect",
                "dns-waf-detect",
                "tech-detect",
                "rdap-whois",
                "spf-record-detect",
                "caa-fingerprint",
                "txt-fingerprint",
                "nameserver-fingerprint",
                "mx-fingerprint",
                "aaaa-fingerprint",
            ],
            "RECON": [
                "ssl-issuer",
                "ssl-dns-names",
                "wildcard-tls",
                "azure-domain-tenant",
                "apache-detect",
                "options-method",
                "form-detection",
                "web-server",
                "exposed",
            ],
            "CONFIGURATION": [
                "http-missing-security-headers",
                "deprecated-tls",
                "tls-version",
                "weak-cipher-suites",
                "ssh-cbc-mode-ciphers",
                "ssh-weak-algo-supported",
                "ssh-weak-mac-algo",
                "ssh-diffie-hellman-logjam",
                "ssh-sha1-hmac-algo",
                "ssh-weakkey-exchange-algo",
                "ssh-auth-methods",
                "ssh-password-auth",
                "ssh-server-enumeration",
            ],
            "VULNERABILITY": ["web-server", "cve", "cwe"],
            "EXPLOITATION": ["sqlmap", "sql injection"],
        }
        self.attack_paths = []
        self.path_scores = {}

    def _normalize_asset_key(self, vulnerability: Dict) -> str:
        candidates = [vulnerability.get("target"), vulnerability.get("evidence")]

        for candidate in candidates:
            if not candidate:
                continue

            text = str(candidate).strip()
            parsed = urlparse(text)
            if parsed.scheme and parsed.netloc:
                return parsed.netloc.split("@")[-1].split(":")[0].lower()

            host = text.split("/")[0].split(":")[0]
            if host:
                return host.lower()

        return "unknown"

    def _normalize_severity(self, severity: str) -> str:
        normalized = str(severity or "Info").strip().capitalize()
        if normalized not in {"Critical", "High", "Medium", "Low", "Info"}:
            return "Info"
        return normalized

    def _severity_score(self, severity: str) -> float:
        return {"Critical": 5.0, "High": 4.0, "Medium": 3.0, "Low": 2.0, "Info": 1.0}.get(
            self._normalize_severity(severity),
            1.0,
        )

    def _classify_stage(self, vulnerability: Dict) -> str:
        component = str(vulnerability.get("component", "")).lower()
        cve_id = str(vulnerability.get("cve_id", "")).lower()
        description = str(vulnerability.get("description", "")).lower()
        source_tool = str(vulnerability.get("source_tool", "")).lower()
        severity = self._normalize_severity(vulnerability.get("severity"))

        combined = " ".join([component, cve_id, description, source_tool])

        for stage, patterns in self.categories.items():
            if any(pattern in combined for pattern in patterns):
                return stage

        if severity == "Critical" or cve_id.startswith("cve-") or cve_id.startswith("cwe-"):
            return "VULNERABILITY"

        if source_tool == "ffuf" or "discovered-path" in cve_id:
            return "RECON"

        if severity == "High":
            return "VULNERABILITY"

        if severity == "Medium":
            return "CONFIGURATION"

        return "INFO_GATHERING"

    def _stage_index(self, stage: str) -> int:
        try:
            return self.category_order.index(stage)
        except ValueError:
            return len(self.category_order)

    def _build_display_name(self, vulnerability: Dict) -> str:
        component = str(vulnerability.get("component", "unknown")).strip() or "unknown"
        cve_id = str(vulnerability.get("cve_id", "N/A")).strip()
        if cve_id and cve_id.upper() != "N/A":
            return f"{component} ({cve_id})"

        source_tool = str(vulnerability.get("source_tool", "")).strip()
        if source_tool:
            return f"{component} [{source_tool}]"

        return component

    def _score_node(self, vulnerability: Dict, stage: str) -> float:
        cvss = vulnerability.get("cvss")
        if cvss is None or cvss == "N/A":
            cvss = 0.0

        try:
            cvss_score = float(cvss)
        except (TypeError, ValueError):
            cvss_score = 0.0

        return self._severity_score(vulnerability.get("severity")) * 10.0 + cvss_score + self._stage_index(stage)

    def _build_path_for_asset(self, asset_nodes: List[tuple]) -> List[str]:
        ordered_nodes = sorted(
            asset_nodes,
            key=lambda item: (
                item[1]["stage_order"],
                -item[1]["risk_score"],
                -item[1]["effective_cvss"],
                item[1]["display_name"].lower(),
            ),
        )

        stage_best = {}
        for node_id, node_data in ordered_nodes:
            stage = node_data["category"]
            if stage not in stage_best:
                stage_best[stage] = (node_id, node_data)

        staged_path = [stage_best[stage] for stage in self.category_order if stage in stage_best]
        if len(staged_path) > 1:
            return [node_data["display_name"] for _, node_data in staged_path]

        fallback_path = []
        seen = set()
        for node_id, node_data in ordered_nodes:
            display_name = node_data["display_name"]
            if display_name in seen:
                continue
            seen.add(display_name)
            fallback_path.append(display_name)

        if len(fallback_path) > 1:
            return fallback_path

        return []

    def _get_category(self, component: str) -> str:
        for cat, components in self.categories.items():
            component_lower = str(component).lower()
            if any(pattern in component_lower for pattern in components):
                return cat
        return "INFO_GATHERING"

    def generate_graph(self, vulnerabilities: List[Dict]):
        self.graph.clear()
        self.attack_paths = []
        self.path_scores = {}

        for i, v in enumerate(vulnerabilities):
            display_name = self._build_display_name(v)
            stage = self._classify_stage(v)
            effective_cvss = v.get("cvss")
            if effective_cvss is None or effective_cvss == "N/A":
                effective_cvss = self._severity_score(v.get("severity")) * 2.0

            try:
                effective_cvss = float(effective_cvss)
            except (TypeError, ValueError):
                effective_cvss = 0.0
            
            node_id = f"v{i}_{display_name}"
            v_enriched = v.copy()
            v_enriched["asset_key"] = self._normalize_asset_key(v)
            v_enriched["effective_cvss"] = effective_cvss
            v_enriched["display_name"] = display_name
            v_enriched["category"] = stage
            v_enriched["stage_order"] = self._stage_index(stage)
            v_enriched["risk_score"] = self._score_node(v, stage)
            self.graph.add_node(node_id, **v_enriched)

        grouped_nodes = defaultdict(list)
        for node_id, node_data in self.graph.nodes(data=True):
            grouped_nodes[node_data["asset_key"]].append((node_id, node_data))

        for asset_key, nodes in grouped_nodes.items():
            ordered_nodes = sorted(
                nodes,
                key=lambda item: (
                    item[1]["stage_order"],
                    -item[1]["risk_score"],
                    -item[1]["effective_cvss"],
                    item[1]["display_name"].lower(),
                ),
            )

            for index in range(len(ordered_nodes) - 1):
                current_id, current_data = ordered_nodes[index]
                next_id, next_data = ordered_nodes[index + 1]

                if current_id == next_id:
                    continue

                edge_label = "risk progression"
                if next_data["stage_order"] > current_data["stage_order"]:
                    edge_label = "logical progression"
                elif next_data["risk_score"] > current_data["risk_score"]:
                    edge_label = "escalation"

                self.graph.add_edge(current_id, next_id, label=edge_label, asset_key=asset_key)

            path = self._build_path_for_asset(ordered_nodes)
            if len(path) > 1:
                self.attack_paths.append(path)
                path_score = sum(node_data["risk_score"] for _, node_data in ordered_nodes) + len(path)
                self.path_scores[tuple(path)] = path_score

        return self.graph

    def get_ranked_chains(self, limit=10):
        ranked = sorted(
            self.attack_paths,
            key=lambda path: (
                self.path_scores.get(tuple(path), 0),
                len(path),
                path[-1].lower(),
            ),
            reverse=True,
        )
        return ranked[:limit]
