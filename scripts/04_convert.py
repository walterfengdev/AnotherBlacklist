import os
import subprocess

def compile_json_to_srs(json_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            json_file = os.path.join(json_dir, filename)
            srs_file = os.path.join(output_dir, filename.replace(".json", ".srs"))
            command = f"sing-box rule-set compile --output {srs_file} {json_file}"
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"Compiled {json_file} to {srs_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error compiling {json_file}: {e}")

def main():
    json_dirs = ["json", "domains"]
    output_dir = "srs"

    for json_dir in json_dirs:
        compile_json_to_srs(json_dir, os.path.join(output_dir, json_dir))

if __name__ == "__main__":
    main()
