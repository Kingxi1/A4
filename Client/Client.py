import socket
import sys

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def get_file(self, fname):
        print(f"Getting {fname}")
        self.sock.sendto(f"DOWNLOAD {fname}".encode(), (self.host, self.port))
        
        try:
            data, _ = self.sock.recvfrom(1024)
            resp = data.decode()
            print(f"Response: {resp}")
        except Exception as e:
            print(f"Error: {e}")
            
    def close(self):
        self.sock.close()


def main():
    
    if len(sys.argv) != 4:
        print("Usage: python UDPclient.py <host> <port> <file_list>")
        return
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    list_file = sys.argv[3]
    
    c = Client(host, port)
    try:
        with open(list_file, 'r') as f:
            for line in f:
                fname = line.strip()
                if fname:
                    c.get_file(fname)
    finally:
        c.close()

if __name__ == "__main__":
    main()