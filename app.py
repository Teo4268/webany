import requests
import time
import signal
import sys

API_URL = "https://engine.hyperbeam.com/v0/vm"
START_URL = "https://akcgh.pages.dev"

# Đọc token từ file nếu có, kết hợp với danh sách token sẵn
try:
    with open("tokens.txt") as f:
        TOKENS = f.read().splitlines()
except FileNotFoundError:
    print("⚠️ File 'tokens.txt' không tồn tại. Sử dụng token mặc định.")
    TOKENS = []

# Token thêm thủ công ở đây
TOKENS += [
    "sk_live_Q2QodCQu_fYfSgykyVoLy4Bj4X1G132k0moZrSFw5s0",
    "sk_live_-FBDxjjgcXDsMdl1-WeenWOIth9iiKbs4AayQR3zcEs",
    # Thêm token khác nếu cần
]

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    END = '\033[0m'

sessions = []

def create_vm(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "start_url": START_URL,
        "timeout": {
            "absolute": 3600,
            "inactive": 3600,
            "offline": 3600,
            "warning": 60,
        },
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        vm_info = resp.json()
        vm_info["token"] = token
        print(f"{Color.GREEN}✔ VM created: {vm_info['session_id']}{Color.END}")
        return vm_info
    except Exception as e:
        print(f"{Color.RED}✘ Failed to create VM: {e}{Color.END}")
        return None

def delete_vm(session_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{API_URL}/{session_id}"
    try:
        resp = requests.delete(url, headers=headers)
        if resp.status_code == 204:
            print(f"{Color.GREEN}✔ VM {session_id} deleted successfully{Color.END}")
        else:
            print(f"{Color.RED}✘ Failed to delete VM {session_id}: {resp.status_code} {resp.text}{Color.END}")
    except Exception as e:
        print(f"{Color.RED}✘ Exception deleting VM {session_id}: {e}{Color.END}")

def ping_vm(embed_url):
    try:
        resp = requests.get(embed_url)
        if resp.status_code == 200:
            print(f"{Color.GREEN}Ping {embed_url} OK{Color.END}")
        else:
            print(f"{Color.YELLOW}Ping {embed_url} returned status {resp.status_code}{Color.END}")
    except Exception as e:
        print(f"{Color.RED}Ping error {embed_url}: {e}{Color.END}")

def exit_handler(sig, frame):
    print(f"\n{Color.YELLOW}Exiting... Deleting all VMs{Color.END}")
    for vm in sessions:
        delete_vm(vm["session_id"], vm["token"])
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    print(f"{Color.YELLOW}Creating 10 VMs per token...{Color.END}")
    for token_index, token in enumerate(TOKENS, start=1):
        print(f"\n{Color.YELLOW}→ Token {token_index}/{len(TOKENS)}: Creating VMs{Color.END}")
        for i in range(10):
            vm = create_vm(token)
            if vm:
                sessions.append(vm)
            else:
                print(f"{Color.RED}✘ Skipping VM {i+1} for token {token_index}{Color.END}")

    if not sessions:
        print(f"{Color.RED}No VMs created. Exiting.{Color.END}")
        return

    print(f"\n{Color.YELLOW}Open these embed URLs in your browser to access the VMs:{Color.END}")
    for i, vm in enumerate(sessions, start=1):
        print(f"VM {i}: {vm['embed_url']}")

    print(f"\n{Color.YELLOW}Starting ping loop every 10 seconds. Press Ctrl+C to stop and delete VMs.{Color.END}")

    while True:
        for vm in sessions:
            ping_vm(vm["embed_url"])
        time.sleep(10)

if __name__ == "__main__":
    main()
