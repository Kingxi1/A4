import socket
import sys
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python UDPserver.py <port>")
        return
        
    port = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    
    print(f"Server listening on port {port}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            req = data.decode().split()
            
            if req[0] == "DOWNLOAD":
                fname = req[1]
                if os.path.exists(fname):
                    size = os.path.getsize(fname)
                    resp = f"OK SIZE {size}"
                    sock.sendto(resp.encode(), addr)
                else:
                    resp = f"ERR {fname} NOT_FOUND"
                    sock.sendto(resp.encode(), addr)
            print(f"Received from {addr}: {data.decode()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()