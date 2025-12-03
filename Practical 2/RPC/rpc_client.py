#!/usr/bin/env python3
import sys
import os
from xmlrpc.client import ServerProxy, Binary


def main():
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <server_host> <server_port> <file_path>")
        print(f"Example: python {sys.argv[0]} 127.0.0.1 8000 /path/to/file.txt")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    file_path = sys.argv[3]

    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        sys.exit(1)

    filename = os.path.basename(file_path)

   
    with open(file_path, "rb") as f:
        data = f.read()

    print(f"[+] Connecting to RPC server at {server_host}:{server_port}")
    url = f"http://{server_host}:{server_port}/RPC2"
    proxy = ServerProxy(url)

    print(f"[+] Sending file {filename} ({len(data)} bytes)")
   
    try:
        result = proxy.upload_file(filename, Binary(data))
        print(f"[+] Server replied: {result}")
    except Exception as e:
        print(f"[!] RPC error: {e}")


if __name__ == "__main__":
    main()
