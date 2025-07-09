import os
import sys
import configparser
import subprocess
import re
import urllib.parse

SESSION_NAME = "POCO X7 PRO"  # <-- Change this to your session name

def get_winscp_ini_path():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("APPDATA environment variable not found.")
        sys.exit(1)
    ini_path = os.path.join(appdata, "WinSCP.ini")
    if not os.path.isfile(ini_path):
        print(f"WinSCP.ini not found at {ini_path}")
        sys.exit(1)
    return ini_path

def is_valid_ipv4(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)

def get_gateway_ips():
    # Use ipconfig to find default gateway(s)
    try:
        output = subprocess.check_output("ipconfig", encoding="utf-8")
    except Exception as e:
        print(f"Failed to run ipconfig: {e}")
        sys.exit(1)
    # Find lines like: "Default Gateway . . . . . . . . . : 192.168.1.1"
    matches = re.findall(r"Default Gateway[ .:]*([\d\.]+)", output)
    # Remove empty, single dot, and duplicate entries; filter for valid IPv4 addresses
    ips = [ip for ip in matches if ip.strip() and ip.strip() != '.' and is_valid_ipv4(ip.strip())]
    return list(dict.fromkeys(ips))

def choose_ip(ips):
    if not ips:
        return None
    if len(ips) == 1:
        print(f"Only one gateway IP found: {ips[0]}")
        return ips[0]
    print("Multiple gateway IPs found:")
    for idx, ip in enumerate(ips):
        print(f"{idx+1}: {ip}")
    while True:
        choice = input(f"Select gateway IP [1-{len(ips)}]: ")
        if choice.isdigit() and 1 <= int(choice) <= len(ips):
            return ips[int(choice)-1]

def main():
    ini_path = get_winscp_ini_path()
    config = configparser.ConfigParser(strict=False)
    config.optionxform = str  # preserve case
    config.read(ini_path, encoding="utf-8")

    # Encode the session name for the INI section
    encoded_session_name = urllib.parse.quote(SESSION_NAME, safe='')
    section = f"Sessions\\{encoded_session_name}"
    if section not in config:
        print(f"Session '{SESSION_NAME}' not found in {ini_path}")
        sys.exit(1)

    ips = get_gateway_ips()
    if not ips:
        print("No gateway IPs found.")
        sys.exit(1)
    gateway_ip = choose_ip(ips)

    config[section]['HostName'] = gateway_ip

    with open(ini_path, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)
    print(f"Updated session '{SESSION_NAME}' HostName to {gateway_ip} in {ini_path}")
    
    # Auto-open WinSCP
    try:
        print("Opening WinSCP...")
        subprocess.Popen([r"C:\Program Files (x86)\WinSCP\WinSCP.exe", SESSION_NAME])
    except Exception:
        print("Failed to open WinSCP. Please open it manually.")

if __name__ == "__main__":
    main()