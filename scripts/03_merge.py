import os
import json

def merge_domains(input_dir):
    domains = set()
    for filename in os.listdir(input_dir):
        if filename.endswith("_domains.txt"):
            with open(os.path.join(input_dir, filename), "r") as f:
                for line in f:
                    domains.add(line.strip().lower())
    return domains

def save_domains(domains, output_filename):
    with open(output_filename, "w") as f:
        for domain in sorted(domains):
            f.write(domain + "\n")

def save_domains_json(domains, output_filename):
    data = {
        "version": 3,
        "rules": [
            {
                "domain_keyword": sorted(list(domains))
            }
        ]
    }
    with open(output_filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    input_dir = "plain"
    output_dir = "domains"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    domains = merge_domains(input_dir)
    save_domains(domains, os.path.join(output_dir, "anotherblacklist.txt"))
    save_domains_json(domains, os.path.join(output_dir, "anotherblacklist.json"))

if __name__ == "__main__":
    main()