import os
import sys
import configparser

try:
    import netifaces
except ImportError:
    print("Please install netifaces: pip install netifaces")
    sys.exit(1)

# Define the session name to update
SESSION_NAME = "POCO%20X7%20PRO"  # <-- Change this to your session name

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

def get_gateway_ips():
    gateways = netifaces.gateways()
    default_gateways = gateways.get('default', {})
    ips = []
    for proto in ('AF_INET', netifaces.AF_INET):
        gw = default_gateways.get(proto)
        if gw:
            ips.append(gw[0])
    # Also collect all gateways from all interfaces
    for proto in (netifaces.AF_INET,):
        for gw in gateways.get(proto, []):
            ips.append(gw[0])
    # Remove duplicates
    return list(dict.fromkeys(ips))

def choose_ip(ips):
    if len(ips) == 1:
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

    section = f"Sessions\\{SESSION_NAME}"
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

if __name__ == "__main__":
    main()
