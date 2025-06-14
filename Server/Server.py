import socket
import sys
import os
import threading    




class FileThread(threading.Thread):
    def __init__(self, addr, port, fname):
        threading.Thread.__init__(self)
        self.addr = addr
        self.port = port
        self.fname = fname
        
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.port))
        
        try:
            with open(self.fname, 'rb') as f:
                while True:
                    data, addr = sock.recvfrom(1024)
                    req = data.decode().split()
                    
                    if req[0] == "FILE" and req[2] == "GET":
                        # 处理文件请求
                        pass
                    elif req[0] == "FILE" and req[2] == "CLOSE":
                        break
                        
        except Exception as e:
            print(f"Error in file transfer: {e}")
        finally:
            sock.close()





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
            print(f"Error in main loop: {e}")

  

if __name__ == "__main__":
    main()