import os
import json

def load_whitelist(filename):
    whitelist = set()
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                domain = parts[0].lower()
                whitelist.add(domain)
    return whitelist

def merge_domains(input_dir, whitelist, upstream_sources):
    domains = {"domain": set(), "domain_suffix": set(), "domain_keyword": set()}
    for filename in os.listdir(input_dir):
        if filename.endswith("_domains.txt"):
            name = filename.replace("_domains.txt", "")
            type = upstream_sources[name]["type"]
            with open(os.path.join(input_dir, filename), "r") as f:
                for line in f:
                    domain = line.strip().lower()
                    if domain not in whitelist:
                        domains[type].add(domain)
    return domains

def save_domains(domains, output_filename):
    with open(output_filename, "w") as f:
        for domain in sorted(domains):
            f.write(domain + "\n")

def save_domains_json(domains, output_filename):
    rules = []
    for type, domain_list in domains.items():
        if domain_list:
            rules.append({type: sorted(list(domain_list))})

    data = {
        "version": 3,
        "rules": rules
    }
    with open(output_filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    input_dir = "plain"
    whitelist_file = "whitelist.txt"
    output_dir = "domains"
    upstream_sources_file = "config.json"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    whitelist = load_whitelist(whitelist_file)
    with open(upstream_sources_file, "r") as f:
        upstream_sources = json.load(f)["sources"]
    domains = merge_domains(input_dir, whitelist, upstream_sources)
    save_domains(set().union(*domains.values()), os.path.join(output_dir, "anotherblacklist.txt"))
    save_domains_json(domains, os.path.join(output_dir, "anotherblacklist.json"))

if __name__ == "__main__":
    main()
