
import socket
import struct
import os

BUFFER_SIZE = 4096

def main():
    import sys

    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <server_host> <server_port> <file_path>")
        return

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    file_path = sys.argv[3]

    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        return

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    print(f"[+] Connecting to {server_host}:{server_port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))
        print("[+] Connected")

        
        filename_bytes = filename.encode("utf-8")
        sock.sendall(struct.pack("!I", len(filename_bytes)))

       
        sock.sendall(filename_bytes)

        
        sock.sendall(struct.pack("!Q", filesize))

        print(f"[+] Sending file: {filename} ({filesize} bytes)")

       
        sent = 0
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)

        print(f"[+] File sent ({filesize} bytes)")

        
        try:
            ack = sock.recv(1024)
            if ack:
                print(f"[+] Server replied: {ack.decode(errors='ignore')}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
