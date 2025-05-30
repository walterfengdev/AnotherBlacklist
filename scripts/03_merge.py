import os
import json

def load_whitelist(filename):
    whitelist = {"exact_domains": set(), "domain_suffixes": set(), "keywords": set()}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue
            if line.startswith("keyword:"):
                keyword = line.replace("keyword:", "").strip()
                if keyword:
                    whitelist["keywords"].add(keyword)
            else:
                # Add to both exact and suffix for now, can be refined if needed
                # For a line like "abcd.com", we want to whitelist "abcd.com" itself
                # and also treat "abcd.com" as a suffix to remove "sub.abcd.com"
                whitelist["exact_domains"].add(line)
                whitelist["domain_suffixes"].add(line)
    return whitelist

def merge_domains(input_dir, whitelist, upstream_sources):
    domains = {"domain": set(), "domain_suffix": set(), "domain_keyword": set()}

    for filename in os.listdir(input_dir):
        if filename.endswith("_domains.txt"):
            name = filename.replace("_domains.txt", "")
            # Ensure the source name exists in upstream_sources to prevent KeyErrors
            if name not in upstream_sources:
                print(f"Warning: Source '{name}' not found in upstream_sources (config.json). Skipping.")
                continue

            source_type = upstream_sources[name]["type"] # domain, domain_suffix, or domain_keyword

            with open(os.path.join(input_dir, filename), "r") as f:
                for line in f:
                    domain = line.strip().lower()
                    if not domain:
                        continue

                    is_whitelisted = False

                    # 1. Check exact domain whitelist
                    if domain in whitelist["exact_domains"]:
                        is_whitelisted = True

                    # 2. Check domain suffix whitelist
                    if not is_whitelisted:
                        for suffix in whitelist["domain_suffixes"]:
                            if domain.endswith("." + suffix) or domain == suffix:
                                is_whitelisted = True
                                break

                    # 3. Check keyword whitelist
                    if not is_whitelisted:
                        for keyword in whitelist["keywords"]:
                            if keyword in domain:
                                is_whitelisted = True
                                break

                    if not is_whitelisted:
                        # Add to the correct type set based on the source's configuration
                        if source_type in domains:
                            domains[source_type].add(domain)
                        else:
                            # Fallback to 'domain' if type is unknown, or handle error
                            print(f"Warning: Unknown type '{source_type}' for source '{name}'. Adding to 'domain' by default.")
                            domains["domain"].add(domain)

    return domains

def save_domains(domains_set, output_filename): # Expects a single set of all domains to save
    with open(output_filename, "w") as f:
        for domain in sorted(list(domains_set)): # Convert set to list before sorting
            f.write(domain + "\n")

def save_domains_json(domains_dict, output_filename): # Expects the dictionary of types and sets
    rules = []
    # Ensure consistent order of rule types in the output JSON
    for type_key in sorted(domains_dict.keys()):
        domain_list = domains_dict[type_key]
        if domain_list: # Only add if the list is not empty
            rules.append({type_key: sorted(list(domain_list))})

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

    whitelist_data = load_whitelist(whitelist_file)

    try:
        with open(upstream_sources_file, "r") as f:
            upstream_sources = json.load(f)["sources"]
    except FileNotFoundError:
        print(f"Error: Upstream sources file '{upstream_sources_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{upstream_sources_file}'.")
        return
    except KeyError:
        print(f"Error: 'sources' key not found in '{upstream_sources_file}'.")
        return

    merged_domains_by_type = merge_domains(input_dir, whitelist_data, upstream_sources)

    all_merged_domains_set = set()
    for domain_set in merged_domains_by_type.values():
        all_merged_domains_set.update(domain_set)

    save_domains(all_merged_domains_set, os.path.join(output_dir, "anotherblacklist.txt"))
    save_domains_json(merged_domains_by_type, os.path.join(output_dir, "anotherblacklist.json"))

    print(f"Whitelist data loaded: {len(whitelist_data['exact_domains'])} exact, {len(whitelist_data['domain_suffixes'])} suffixes, {len(whitelist_data['keywords'])} keywords.")
    print(f"Merging complete. Output files are in '{output_dir}' directory.")
    for type_key, domain_s in merged_domains_by_type.items():
        print(f"  Type '{type_key}': {len(domain_s)} domains")

if __name__ == "__main__":
    main()