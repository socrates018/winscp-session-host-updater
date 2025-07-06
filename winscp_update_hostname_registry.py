import os
import sys
import subprocess
import re
import urllib.parse
import winreg

SESSION_NAME = "POCO X7 PRO"  # <-- Change this to your session name

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

def update_winscp_session_registry(session_name, hostname):
    # WinSCP stores sessions in HKEY_CURRENT_USER\Software\Martin Prikryl\WinSCP 2\Sessions
    base_key = r"Software\Martin Prikryl\WinSCP 2\Sessions"
    
    # URL encode the session name for registry key
    encoded_session_name = urllib.parse.quote(session_name, safe='')
    
    try:
        # Open the registry key for the specific session
        session_key_path = f"{base_key}\\{encoded_session_name}"
        
        # Try to open the existing session key
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, session_key_path, 0, winreg.KEY_SET_VALUE) as key:
            # Set the HostName value
            winreg.SetValueEx(key, "HostName", 0, winreg.REG_SZ, hostname)
            print(f"Updated session '{session_name}' HostName to {hostname} in registry")
            
    except FileNotFoundError:
        print(f"Session '{session_name}' not found in registry at {session_key_path}")
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Try running as administrator.")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating registry: {e}")
        sys.exit(1)

def main():
    ips = get_gateway_ips()
    if not ips:
        print("No gateway IPs found.")
        sys.exit(1)
    gateway_ip = choose_ip(ips)
    
    if not gateway_ip:
        print("No valid gateway IP selected.")
        sys.exit(1)
    
    update_winscp_session_registry(SESSION_NAME, gateway_ip)

if __name__ == "__main__":
    main()
