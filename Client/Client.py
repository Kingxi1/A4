import socket
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python UDPclient.py <host> <port> <file_list>")
        return
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    list_file = sys.argv[3]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b"Hello", (host, port))
    
    try:
        data, _ = sock.recvfrom(1024)
        print(f"Received: {data.decode()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()