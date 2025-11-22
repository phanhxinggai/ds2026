
import socket
import struct
import os

HOST = "0.0.0.0"  # lắng nghe trên mọi interface
BUFFER_SIZE = 4096

def recv_exact(conn, length):
    
    data = b""
    while len(data) < length:
        chunk = conn.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data

def handle_client(conn, addr):
    print(f"[+] Connected from {addr}")

    
    raw = recv_exact(conn, 4)
    filename_len = struct.unpack("!I", raw)[0]

   
    filename_bytes = recv_exact(conn, filename_len)
    filename = filename_bytes.decode("utf-8")

    
    raw = recv_exact(conn, 8)
    filesize = struct.unpack("!Q", raw)[0]

    print(f"[+] Receiving file: {filename} ({filesize} bytes)")

    safe_filename = "received_" + os.path.basename(filename)
    received = 0

    with open(safe_filename, "wb") as f:
        while received < filesize:
            chunk = conn.recv(min(BUFFER_SIZE, filesize - received))
            if not chunk:
                raise ConnectionError("Connection closed while receiving file data")
            f.write(chunk)
            received += len(chunk)

    print(f"[+] File saved as {safe_filename} ({received} bytes)")

    
    conn.sendall(b"OK")

def main():
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <port>")
        return

    port = int(sys.argv[1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, port))
        server_sock.listen(1)  
        print(f"[+] Server listening on {HOST}:{port}")

        while True:
            conn, addr = server_sock.accept()
            with conn:
                try:
                    handle_client(conn, addr)
                except Exception as e:
                    print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
