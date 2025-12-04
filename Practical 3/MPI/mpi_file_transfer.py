from mpi4py import MPI
import os
import sys

CHUNK_SIZE = 4096  

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def sender(file_path: str):
    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        return

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    print(f"[Sender] Will send file: {filename} ({filesize} bytes) to rank 1")

    
    comm.send(filename, dest=1, tag=0)   # tag 0: filename
    comm.send(filesize, dest=1, tag=1)   # tag 1: filesize

  
    sent = 0
    with open(file_path, "rb") as f:
        while sent < filesize:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            comm.Send([bytearray(chunk), MPI.BYTE], dest=1, tag=2)
            sent += len(chunk)

    print(f"[Sender] Done. Sent {sent} bytes.")


def receiver():
    
   
    filename = comm.recv(source=0, tag=0)   
    filesize = comm.recv(source=0, tag=1)   

    safe_filename = "received_" + os.path.basename(filename)
    print(f"[Receiver] Receiving file: {filename} ({filesize} bytes)")
    print(f"[Receiver] Saving as: {safe_filename}")

    received = 0
    with open(safe_filename, "wb") as f:
        while received < filesize:
            
            remaining = filesize - received
            current_chunk_size = min(CHUNK_SIZE, remaining)

            buf = bytearray(current_chunk_size)
            comm.Recv([buf, MPI.BYTE], source=0, tag=2)
            f.write(buf)
            received += len(buf)

    print(f"[Receiver] Done. Received {received} bytes.")


def main():
    if size != 2:
        if rank == 0:
            print("[!] This program must be run with exactly 2 MPI processes.")
            print("    Example: mpiexec -n 2 python mpi_file_transfer.py <file_path>")
        return

    
    if rank == 0:
        if len(sys.argv) != 2:
            print(f"Usage: mpiexec -n 2 python {sys.argv[0]} <file_path>")
            return
        file_path = sys.argv[1]
        sender(file_path)
    elif rank == 1:
        receiver()
    else:
        pass


if __name__ == "__main__":
    main()
