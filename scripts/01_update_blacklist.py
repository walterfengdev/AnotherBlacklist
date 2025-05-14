import requests
import os

# Define upstream sources
upstream_sources = {
    "StevenBlack": "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-only/hosts",
    "1Host": "https://raw.githubusercontent.com/badmojr/1Hosts/master/Pro/domains.wildcards",
    "Hagezi_gambling": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/gambling-onlydomains.txt",
    "BrigsLabs_gambling": "https://raw.githubusercontent.com/BrigsLabs/judol/refs/heads/main/judol_domains.txt",
    "ut1_gambling": "https://github.com/olbat/ut1-blacklists/raw/refs/heads/master/blacklists/gambling/domains",
    "oisd_big": "https://big.oisd.nl/dnsmasq",
    "Hagezi_pro": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/dnsmasq/pro.txt",
    "Hagezi_tif": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/tif-onlydomains.txt",
    "Hagezi_piracy": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/anti.piracy-onlydomains.txt",
    "ut1_dating": "https://raw.githubusercontent.com/olbat/ut1-blacklists/refs/heads/master/blacklists/dating/domains",
    "xRuffKez_NRD14day": "https://github.com/xRuffKez/NRD/raw/refs/heads/main/lists/14-day/domains-only/nrd-14day.txt"
}

def download_blocklists():
    src_dir = "src"
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)

    for name, url in upstream_sources.items():
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
    download_blocklists()