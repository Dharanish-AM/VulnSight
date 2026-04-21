from app.attack_graph.attack_chain import AttackGraphEngine


def test_attack_paths_group_findings_by_asset_and_stage():
    engine = AttackGraphEngine()

    vulnerabilities = [
        {
            "target": "http://scanme.nmap.org",
            "cve_id": "N/A",
            "severity": "Info",
            "cvss": 0.0,
            "description": "A web application firewall was detected.",
            "component": "waf-detect",
            "evidence": "scanme.nmap.org",
            "source_tool": "nuclei",
        },
        {
            "target": "scanme.nmap.org",
            "cve_id": "DISCOVERED-PATH",
            "severity": "Low",
            "cvss": 2.0,
            "description": "Exposed resource found via fuzzing: http://scanme.nmap.org/images/",
            "component": "Web Server",
            "evidence": "Status 200 at http://scanme.nmap.org/images/",
            "source_tool": "ffuf",
        },
        {
            "target": "scanme.nmap.org",
            "cve_id": "CVE-2024-38474",
            "severity": "Medium",
            "cvss": 9.8,
            "description": "Found via nmap vulners script: CVE-2024-38474",
            "component": "http",
            "evidence": "Port 80 open",
            "source_tool": "nmap",
        },
    ]

    engine.generate_graph(vulnerabilities)
    attack_paths = engine.get_ranked_chains()

    assert attack_paths, "expected at least one attack path"
    assert any("waf-detect" in node for node in attack_paths[0])
    assert any("Web Server" in node or "http" in node for node in attack_paths[0])