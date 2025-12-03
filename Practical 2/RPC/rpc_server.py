#!/usr/bin/env python3
import sys
import os
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import Binary

UPLOAD_DIR = "uploads"


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


def upload_file(filename, data):
    """
    RPC method: nhận file từ client và lưu vào UPLOAD_DIR.
    filename: str
    data: xmlrpc.client.Binary
    """
    if not isinstance(data, Binary):
        return "ERROR: data must be xmlrpc.client.Binary"

    
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    safe_name = os.path.basename(filename)
    dest_path = os.path.join(UPLOAD_DIR, safe_name)

    file_bytes = data.data
    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    return f"OK: saved {safe_name} ({len(file_bytes)} bytes)"


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <host> <port>")
        print(f"Example: python {sys.argv[0]} 0.0.0.0 8000")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    with SimpleXMLRPCServer((host, port),
                            requestHandler=RequestHandler,
                            allow_none=False) as server:
        server.register_introspection_functions()

       
        server.register_function(upload_file, "upload_file")

        print(f"[+] RPC server listening on {host}:{port}")
        print(f"[+] Files will be stored in: {os.path.abspath(UPLOAD_DIR)}")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[+] Server stopped.")


if __name__ == "__main__":
    main()
