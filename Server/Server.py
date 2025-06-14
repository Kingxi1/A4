import socket
import sys

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
            print(f"Received from {addr}: {data.decode()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()