import socket
import sys
import time
import base64


BUFFER_SIZE = 8192  
CHUNK_SIZE = 4096  
MAX_RETRIES = 5     
INITIAL_TIMEOUT = 1.0
MAX_TIMEOUT = 16.0
RETRY_DELAY = 0.1
   

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
        
        self.timeout = INITIAL_TIMEOUT
        self.buffer = bytearray(BUFFER_SIZE)

    def send_recv(self, msg, addr=None):
        if addr is None:
            addr = (self.host, self.port)
            
        retries = 0
        while retries < MAX_RETRIES:
            try:
                self.sock.sendto(msg.encode(), addr)
                self.sock.settimeout(self.timeout)
                data, _ = self.sock.recvfrom(BUFFER_SIZE)
                return data.decode()
            except socket.timeout:
                retries += 1
                self.timeout = min(self.timeout * 2, MAX_TIMEOUT)
                print(f"Timeout, retry {retries}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY)
            except socket.error as e:
                retries += 1
                print(f"Socket error: {e}, retry {retries}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY)
                
        raise Exception("Too many retries")
        
    def get_file(self, fname):
        print(f"Getting {fname}")
        start_time = time.time()
        
        try:
       
            resp = self.send_recv(f"DOWNLOAD {fname}")
            parts = resp.split()
            
            if parts[0] == "ERR":
                print(f"Error: {resp}")
                return False
            
            try:
                size_idx = parts.index("SIZE")
                port_idx = parts.index("PORT")
                
                size = int(parts[size_idx + 1])
                port = int(parts[port_idx + 1])
                
                print(f"Size: {size}")
                print(f"Port: {port}")
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
                addr = (self.host, port)
                
                with open(fname, 'wb') as f:
                    got = 0
                    last_progress = 0
                    retries = 0
                    
                    while got < size:
                        start = got
                        end = min(start + CHUNK_SIZE - 1, size - 1)
                        
                        try:
                            req = f"FILE {fname} GET START {start} END {end}"
                            resp = self.send_recv(req, addr, retries)
                            
                            parts = resp.split()
                            if parts[0] == "FILE" and parts[2] == "OK":
                                data_idx = parts.index("DATA")
                                data = base64.b64decode(parts[data_idx + 1])
                                f.write(data)
                                got += len(data)
                                retries = 0  # Reset retry counter
                                
                                # Show progress
                                progress = (got * 100) // size
                                if progress > last_progress:
                                    print(f"\rProgress: {progress}%", end="", flush=True)
                                    last_progress = progress
                            else:
                                print(f"\nUnexpected response: {resp}")
                                retries += 1
                                if retries >= MAX_RETRIES:
                                    raise Exception("Too many retries")
                                time.sleep(RETRY_DELAY)
                                
                        except Exception as e:
                            print(f"\nError during transfer: {e}")
                            retries += 1
                            if retries >= MAX_RETRIES:
                                raise
                            time.sleep(RETRY_DELAY)
                            
                    print("\nDone")
                    
                    # Calculate transfer speed
                    elapsed = time.time() - start_time
                    speed = size / elapsed if elapsed > 0 else 0
                    print(f"Speed: {speed:.2f} bytes/sec")
                    
                    # Close connection
                    try:
                        req = f"FILE {fname} CLOSE"
                        sock.sendto(req.encode(), addr)
                        sock.settimeout(self.timeout)
                        resp, _ = sock.recvfrom(BUFFER_SIZE)
                        if resp.decode().split()[2] == "CLOSE_OK":
                            print("Closed")
                    except socket.timeout:
                        print("No close confirm")
                    except Exception as e:
                        print(f"Error during close: {e}")
                        
                sock.close()
                return True
                
            
            except Exception as e:
                print(f"Error: {e}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
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
        c.get_files(list_file)
    finally:
        c.close()

if __name__ == "__main__":
    main()