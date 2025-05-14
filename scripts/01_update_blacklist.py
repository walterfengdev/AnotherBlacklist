import requests
import os
import json

def load_upstream_sources(filename):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data["sources"]
    except json.JSONDecodeError as e:
        print(f"Error loading upstream sources: {e}")
        return {}

upstream_sources = load_upstream_sources("upstream_src.json")

def download_blocklists():
    src_dir = "src"
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)

    for name, info in upstream_sources.items():
        url = info["url"]
        filename = f"{src_dir}/{name}.txt"
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(filename, "w") as f:
                f.write(response.text)
            print(f"Updated {name} blocklist")
        except requests.RequestException as e:
            print(f"Error updating {name} blocklist: {e}")

if __name__ == "__main__":
    if upstream_sources:
        download_blocklists()
    else:
        print("No upstream sources loaded.")