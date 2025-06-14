import socket
import sys
import time
import base64


BUFFER_SIZE = 8192  
CHUNK_SIZE = 4096  
MAX_RETRIES = 5     
TIMEOUT = 1.0       

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
        
        self.timeout = TIMEOUT
        self.max_retries = MAX_RETRIES

    def send_recv(self, msg, addr=None):
        if addr is None:
            addr = (self.host, self.port)
            
        retries = 0
        while retries < self.max_retries:
            try:
                self.sock.sendto(msg.encode(), addr)
                self.sock.settimeout(self.timeout)
                data, _ = self.sock.recvfrom(1024)
                return data.decode()
            except socket.timeout:
                retries += 1
                self.timeout = min(self.timeout * 2, 16.0)
                print(f"Timeout, retry {retries}/{self.max_retries}")
                
        raise Exception("Too many retries")
        
    def get_file(self, fname):
        print(f"Getting {fname}")
        start_time = time.time()
        
        try:
       
            resp = self.send_recv(f"DOWNLOAD {fname}")
            parts = resp.split()
            
            if parts[0] == "OK":
                size = int(parts[2])
                port = int(parts[4])
                print(f"Size: {size}")
                
         
                file_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                file_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
                file_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
                
                with open(fname, 'wb') as f:
                    got = 0
                    last_progress = 0
                    
                    while got < size:
                    
                        file_sock.sendto(f"FILE {fname} GET".encode(), (self.host, port))
                        
                 
                        data, _ = file_sock.recvfrom(BUFFER_SIZE)
                        resp = data.decode()
                        
                        if resp.startswith("FILE DONE"):
                            break
                            
                        
                        chunk = base64.b64decode(resp)
                        f.write(chunk)
                        got += len(chunk)
                        
                    
                        progress = (got * 100) // size
                        if progress > last_progress:
                            print(f"\rProgress: {progress}%", end="", flush=True)
                            last_progress = progress
                            
                    print("\nDone")
                    
                    
                    elapsed = time.time() - start_time
                    speed = size / elapsed if elapsed > 0 else 0
                    print(f"Speed: {speed:.2f} bytes/sec")
                    
                
                file_sock.sendto(f"FILE {fname} CLOSE".encode(), (self.host, port))
                file_sock.close()
                
            else:
                print(f"Error: {resp}")
                
        except Exception as e:
            print(f"Error: {e}")
            return False


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