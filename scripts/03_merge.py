import os
import json

def load_whitelist(filename):
    whitelist = {"exact_domains": set(), "domain_suffixes": set(), "keywords": set()}
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("keyword:"):
                    keyword = line.replace("keyword:", "").strip()
                    if keyword:
                        whitelist["keywords"].add(keyword)
                elif line.startswith("full:"):
                    domain = line.replace("full:", "").strip()
                    if domain:
                        whitelist["exact_domains"].add(domain)
                else:
                    # For lines without "full:" or "keyword:", treat as both exact and suffix
                    if line:
                        whitelist["exact_domains"].add(line)
                        whitelist["domain_suffixes"].add(line)
    except FileNotFoundError:
        print(f"Warning: Whitelist file '{filename}' not found. Proceeding with an empty whitelist.")
    return whitelist

def merge_domains(input_dir, whitelist, upstream_sources):
    # Initialize domains dictionary with all expected types to avoid KeyError later
    # The types are 'domain', 'domain_suffix', 'domain_keyword' as seen in config.json
    # and potentially used in the source files.
    domains = {"domain": set(), "domain_suffix": set(), "domain_keyword": set()}

    processed_files_count = 0
    for filename in os.listdir(input_dir):
        if filename.endswith("_domains.txt"):
            processed_files_count += 1
            name = filename.replace("_domains.txt", "")

            if name not in upstream_sources:
                print(f"Warning: Source '{name}' from file '{filename}' not found in upstream_sources (config.json). Skipping.")
                continue

            source_info = upstream_sources[name]
            source_type = source_info.get("type") # domain, domain_suffix, or domain_keyword

            if not source_type:
                print(f"Warning: 'type' not defined for source '{name}' in config.json. Skipping '{filename}'.")
                continue
            if source_type not in domains:
                print(f"Warning: Unknown type '{source_type}' for source '{name}' in '{filename}'. Expected one of {list(domains.keys())}. Skipping.")
                continue

            try:
                with open(os.path.join(input_dir, filename), "r") as f:
                    for line_number, line_content in enumerate(f, 1):
                        domain = line_content.strip().lower()
                        if not domain:
                            continue

                        is_whitelisted = False

                        # 1. Check exact domain whitelist (covers "full:" and regular entries)
                        if domain in whitelist["exact_domains"]:
                            is_whitelisted = True

                        # 2. Check domain suffix whitelist (only for entries not prefixed with "full:")
                        if not is_whitelisted:
                            for suffix in whitelist["domain_suffixes"]:
                                # Ensure suffix itself is not empty and domain is not identical to suffix if already checked by exact_domains
                                if suffix and (domain.endswith("." + suffix) or domain == suffix):
                                    is_whitelisted = True
                                    break

                        # 3. Check keyword whitelist
                        if not is_whitelisted:
                            for keyword in whitelist["keywords"]:
                                if keyword and keyword in domain: # Ensure keyword is not empty
                                    is_whitelisted = True
                                    break

                        if not is_whitelisted:
                            domains[source_type].add(domain)
            except FileNotFoundError:
                print(f"Warning: File '{os.path.join(input_dir, filename)}' not found during merge. Skipping.")
            except Exception as e:
                print(f"Error processing file '{os.path.join(input_dir, filename)}': {e}")

    if processed_files_count == 0:
        print(f"Warning: No '_domains.txt' files found in input directory '{input_dir}'.")

    return domains

def save_domains(domains_set, output_filename):
    try:
        with open(output_filename, "w") as f:
            for domain in sorted(list(domains_set)):
                f.write(domain + "\n")
    except IOError as e:
        print(f"Error saving domains to '{output_filename}': {e}")


def save_domains_json(domains_dict, output_filename):
    rules = []
    for type_key in sorted(domains_dict.keys()):
        domain_list = domains_dict[type_key]
        if domain_list:
            rules.append({type_key: sorted(list(domain_list))})

    data = {
        "version": 3,
        "rules": rules
    }
    try:
        with open(output_filename, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving JSON domains to '{output_filename}': {e}")


def main():
    input_dir = "plain"
    whitelist_file = "whitelist.txt" # file path is relative to where the script is run
    output_dir = "domains"
    upstream_sources_file = "config.json" # file path is relative

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"Error: Could not create output directory '{output_dir}': {e}")
            return

    whitelist_data = load_whitelist(whitelist_file)

    try:
        with open(upstream_sources_file, "r") as f:
            config_data = json.load(f)
            if "sources" not in config_data:
                print(f"Error: 'sources' key not found in '{upstream_sources_file}'.")
                return
            upstream_sources = config_data["sources"]
    except FileNotFoundError:
        print(f"Error: Upstream sources file '{upstream_sources_file}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from '{upstream_sources_file}': {e}")
        return

    # Check if input_dir exists
    if not os.path.exists(input_dir) or not os.listdir(input_dir):
        print(f"Warning: Input directory '{input_dir}' is empty or does not exist. Output might be empty.")
        # Optionally, create dummy empty files if this is a fatal error for downstream processes
        # For now, it will just produce empty output files.

    merged_domains_by_type = merge_domains(input_dir, whitelist_data, upstream_sources)

    all_merged_domains_set = set()
    for domain_set in merged_domains_by_type.values():
        all_merged_domains_set.update(domain_set)

    output_txt_file = os.path.join(output_dir, "anotherblacklist.txt")
    output_json_file = os.path.join(output_dir, "anotherblacklist.json")

    save_domains(all_merged_domains_set, output_txt_file)
    save_domains_json(merged_domains_by_type, output_json_file)

    print(f"Whitelist data loaded: {len(whitelist_data['exact_domains'])} exact domains, {len(whitelist_data['domain_suffixes'])} domain suffixes, {len(whitelist_data['keywords'])} keywords.") #
    print(f"Merging complete. Output files are '{output_txt_file}' and '{output_json_file}'.")
    total_domains_merged = 0
    for type_key, domain_s in merged_domains_by_type.items():
        count = len(domain_s)
        print(f"  Type '{type_key}': {count} domains")
        total_domains_merged += count
    print(f"Total unique domains in blacklist: {len(all_merged_domains_set)}")


if __name__ == "__main__":
    main()