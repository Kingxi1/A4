import socket
import sys
import os
import threading    
import base64
from threading import Lock
import time
import random

# Performance optimization settings
BUFFER_SIZE = 8192  # Increase buffer size
CHUNK_SIZE = 4096   # Increase chunk size
MAX_RETRIES = 3     # Maximum retry attempts
RETRY_DELAY = 0.1   # Retry delay (seconds)
thread_count = 0    # Current thread count
thread_lock = Lock()  # Thread count lock    


class FileThread(threading.Thread):
    def __init__(self, addr, port, fname):
        threading.Thread.__init__(self)
        self.addr = addr
        self.port = port
        self.fname = fname
        
    def run(self):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
                self.sock.bind(('', self.port))
        
    
                with open(self.fname, 'rb') as f:
                    while True:
                        try:
                            data, addr = self.sock.recvfrom(BUFFER_SIZE)
                            req = data.decode().split()
                    
                            if req[0] == "FILE" and req[2] == "GET":
                                start = int(req[4])
                                end = int(req[6])

                                f.seek(start)
                                chunk = f.read(end - start + 1)
                                encoded = base64.b64encode(chunk).decode()
                                
                                
                                resp = f"FILE {self.fname} OK START {start} END {end} DATA {encoded}"
                                self.sock.sendto(resp.encode(), addr)
                                
                            elif req[0] == "FILE" and req[2] == "CLOSE":
                                resp = f"FILE {self.fname} CLOSE_OK"
                                self.sock.sendto(resp.encode(), addr)
                                time.sleep(0.1)
                                return  # Successfully completed, exit thread
                                
                        except socket.error as e:
                            print(f"Socket error in file transfer: {e}")
                            break
                            
            except Exception as e:
                print(f"Error in file transfer: {e}")
                retries += 1
                if retries < MAX_RETRIES:
                    print(f"Retrying... ({retries}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"Max retries reached for {self.fname}")
            finally:
                if self.sock:
                    try:
                        self.sock.close()
                    except:
                        pass
def find_available_port(start_port, end_port):
    """Find an available port in the specified range"""
    max_attempts = 100  # Maximum attempts to find a port
    attempts = 0
    
    while attempts < max_attempts:
        port = random.randint(start_port, end_port)
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_sock.bind(('', port))
            test_sock.close()
            return port
        except:
            attempts += 1
            continue
    
    raise Exception("No available ports found")

def main():
    if len(sys.argv) != 2:
        print("Usage: python UDPserver.py <port>")
        return
        
    port = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
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
                    try:
                        new_port = find_available_port(50000, 51000)
                        print(f"Starting transfer of {fname} on port {new_port}")
                        
                        resp = f"OK {fname} SIZE {size} PORT {new_port}"
                        sock.sendto(resp.encode(), addr)
                        
                        thread = FileThread(addr[0], new_port, fname)
                        thread.start()
                    except Exception as e:
                        print(f"Error starting transfer: {e}")
                        resp = f"ERR {fname} INTERNAL_ERROR"
                        sock.sendto(resp.encode(), addr)
                else:
                    resp = f"ERR {fname} NOT_FOUND"
                    sock.sendto(resp.encode(), addr)

        except Exception as e:
            print(f"Error in main loop: {e}")

  

if __name__ == "__main__":
    main()