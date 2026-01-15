# --- mgmt.py ---
import socket, time

class MgmtError(Exception): pass

def mgmt_send(host: str, port: int, line: str, timeout=2.0) -> str:
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall((line.strip() + "\n").encode())
            time.sleep(0.05)
            chunks = []
            s.settimeout(timeout)
            while True:
                try:
                    chunk = s.recv(8192)
                    if not chunk: break
                    chunks.append(chunk)
                    if b"END" in chunk or b"SUCCESS" in chunk:  # loose stop
                        break
                except socket.timeout:
                    break
    except Exception as e:
        raise MgmtError(f"mgmt({line}) failed: {e}")
    return b"".join(chunks).decode(errors="ignore")

def parse_state(text: str) -> str:
    # returns OPENVPN state code like CONNECTED|RECONNECTING|ASSIGN_IP|...
    for line in text.splitlines():
        if line.startswith(">STATE:"):
            parts = line.split(",")
            if len(parts) >= 2:
                return parts[1]
    return "UNKNOWN"

def wait_for_state(check_fn, target=("CONNECTED","RECONNECTED"), deadline_s=30, sleep_s=0.5) -> bool:
    t0 = time.time()
    while time.time() - t0 < deadline_s:
        if check_fn() in target:
            return True
        time.sleep(sleep_s)
    return False
