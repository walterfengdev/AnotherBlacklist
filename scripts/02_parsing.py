import os
import re
import json

def load_upstream_sources(filename):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data["sources"]
    except json.JSONDecodeError as e:
        print(f"Error loading upstream sources: {e}")
        return {}

def parse_domains(filename, format, domain_index):
    try:
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
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return set()

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
    upstream_sources = load_upstream_sources("config.json")
    if not upstream_sources:
        print("No upstream sources loaded.")
        return

    if not os.path.exists(plain_dir):
        os.makedirs(plain_dir)

    json_dir = "json"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    for name, info in upstream_sources.items():
        format = info["format"]
        domain_index = info["domain_index"]
        filename = f"{src_dir}/{name}.txt"
        domains = parse_domains(filename, info["format"], info["domain_index"])
        if domains:
            save_domains(domains, f"{plain_dir}/{name}_domains.txt")
            save_domains_json(domains, f"{json_dir}/{name}_domains.json")
            print(f"Processed {name} blocklist.")

if __name__ == "__main__":
    main()