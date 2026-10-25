#!/usr/bin/env python3
"""AI-assisted incident analysis: reads error logs from Elasticsearch
and asks an LLM for classification, severity, root cause and remediation."""
import json
import os
import urllib.request

ES_URL = os.getenv("ES_URL", "http://localhost:9200")
API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")


def fetch_logs():
    query = {
        "size": 50,
        "sort": [{"@timestamp": "desc"}],
        "query": {
            "bool": {
                "must": [{"query_string": {"query": "message:(404 OR 500 OR 502 OR 503 OR error)"}}],
                "filter": [{"range": {"@timestamp": {"gte": "now-1h"}}}],
            }
        },
    }
    req = urllib.request.Request(
        ES_URL + "/filebeat-*/_search",
        data=json.dumps(query).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        hits = json.load(resp)["hits"]["hits"]
    return [h["_source"].get("message", "") for h in hits]


def ask_claude(logs):
    prompt = (
        "You are a DevOps incident analyst. Analyze these Nginx logs from an e-commerce website. "
        "Reply with ONLY a JSON object with these keys: error_classification, "
        "severity (Low/Medium/High/Critical), possible_root_cause, "
        "suggested_remediation (a list of short steps).\n\nLOGS:\n" + "\n".join(logs)
    )
    body = {"model": MODEL, "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = json.load(resp)["content"][0]["text"]
    return text.replace("```json", "").replace("```", "").strip()


def rule_based(logs):
    n404 = sum(1 for l in logs if " 404 " in l or "No such file" in l)
    n5xx = sum(1 for l in logs if any(f" {c} " in l for c in ("500", "502", "503")))
    if n5xx:
        result = {
            "error_classification": "Server errors (5xx)",
            "severity": "High",
            "possible_root_cause": "Backend or upstream service failure",
            "suggested_remediation": ["Check pod/container status", "Review recent deployments", "Roll back if needed"],
        }
    elif n404:
        result = {
            "error_classification": "Missing resources (404)",
            "severity": "Medium",
            "possible_root_cause": "A page or file is missing from the deployed image, or broken links",
            "suggested_remediation": ["Check the files inside the container", "Verify the last build", "Redeploy the previous image"],
        }
    else:
        result = {"error_classification": "Unknown", "severity": "Low",
                  "possible_root_cause": "Not enough data", "suggested_remediation": ["Collect more logs"]}
    return json.dumps(result, indent=2)


def main():
    logs = fetch_logs()
    if not logs:
        print("No error logs found in the last hour.")
        return
    print(f"Collected {len(logs)} error log lines.")
    if API_KEY:
        print("Mode: AI (Claude API)\n")
        try:
            print(ask_claude(logs))
            return
        except Exception as exc:
            print(f"AI call failed ({exc}); using rule-based fallback.\n")
    else:
        print("Mode: rule-based fallback (no ANTHROPIC_API_KEY set)\n")
    print(rule_based(logs))


if __name__ == "__main__":
    main()
