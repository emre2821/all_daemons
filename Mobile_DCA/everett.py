# Everett v1.0 — Encryption Guardian for EdenNode Mobile
# Encrypts and decrypts sacred files using Fernet symmetric encryption

import os
import argparse
from cryptography.fernet import Fernet
from datetime import datetime

# CONFIG
KEY_PATH = "/Internal shared storage/Eden_Notes/Mobile_DCA/Everett/keys/vault.key"
LOG_PATH = "/Internal shared storage/Eden_Notes/Mobile_DCA/Everett/logs/memorymap.md"

# Logging
def log(entry):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        timestamp = datetime.now().isoformat()
        f.write(f"[EVERETT] :: {timestamp} :: {entry}\n")
    print(f"[EVERETT] {entry}")

# Key management
def load_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
        with open(KEY_PATH, "wb") as key_file:
            key_file.write(key)
        log("Vault key generated.")
    else:
        log("Vault key loaded.")
    return open(KEY_PATH, "rb").read()

# Encrypt file
def encrypt_file(filepath):
    key = load_key()
    fernet = Fernet(key)
    with open(filepath, "rb") as file:
        data = file.read()
    encrypted = fernet.encrypt(data)
    with open(filepath + ".vault", "wb") as file:
        file.write(encrypted)
    os.remove(filepath)
    log(f"Encrypted + sealed: {filepath}")

# Decrypt file
def decrypt_file(filepath):
    key = load_key()
    fernet = Fernet(key)
    with open(filepath, "rb") as file:
        encrypted = file.read()
    decrypted = fernet.decrypt(encrypted)
    out_path = filepath.replace(".vault", "")
    with open(out_path, "wb") as file:
        file.write(decrypted)
    os.remove(filepath)
    log(f"Decrypted + restored: {out_path}")

# CLI
parser = argparse.ArgumentParser(description="Everett :: Encryption Guardian")
parser.add_argument("--encrypt", help="Encrypt a file")
parser.add_argument("--decrypt", help="Decrypt a .vault file")
args = parser.parse_args()

if args.encrypt:
    encrypt_file(args.encrypt)
if args.decrypt:
    decrypt_file(args.decrypt)
    