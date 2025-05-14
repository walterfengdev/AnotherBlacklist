import os
import re
import json

# Define the upstream sources and their formats
upstream_sources = {
    "StevenBlack": {"format": "hosts", "domain_index": 1},
    "1Host": {"format": "domains", "domain_index": 0},
    "Hagezi_gambling": {"format": "domains", "domain_index": 0},
    "BrigsLabs_gambling": {"format": "domains", "domain_index": 0},
    "ut1_gambling": {"format": "domains", "domain_index": 0},
    "oisd_big": {"format": "dnsmasq", "domain_index": 1},
    "Hagezi_pro": {"format": "dnsmasq", "domain_index": 1},
    "Hagezi_tif": {"format": "domains", "domain_index": 0},
    "Hagezi_piracy": {"format": "domains", "domain_index": 0},
    "ut1_dating": {"format": "domains", "domain_index": 0},
}

def parse_domains(filename, format, domain_index):
    domains = set()
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if format == "hosts":
                parts = line.split()
                if len(parts) > domain_index and parts[0].startswith("0.0.0.0"):
                    domains.add(parts[domain_index])
            elif format == "domains":
                if line and not line.startswith("#"):
                    domains.add(line)
            elif format == "dnsmasq":
                match = re.match(r"server=/([^/]+)/", line)
                if match:
                    domains.add(match.group(1))
                match = re.match(r"local=/([^/]+)/", line)
                if match:
                    domains.add(match.group(1))
    return domains

def save_domains(domains, output_filename):
    with open(output_filename, "w") as f:
        for domain in domains:
            f.write(domain + "\n")

def save_domains_json(domains, output_filename):
    data = {
        "version": 3,
        "rules": [
            {
                "domain_keyword": list(domains)
            }
        ]
    }
    with open(output_filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    src_dir = "src"
    plain_dir = "plain"
    if not os.path.exists(plain_dir):
        os.makedirs(plain_dir)

    json_dir = "json"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    for name, info in upstream_sources.items():
        filename = f"{src_dir}/{name}.txt"
        domains = parse_domains(filename, info["format"], info["domain_index"])
        save_domains(domains, f"{plain_dir}/{name}_domains.txt")
        save_domains_json(domains, f"{json_dir}/{name}_domains.json")

if __name__ == "__main__":
    main()