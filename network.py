import socket
import pickle

class Network:
    def __init__(self, server="localhost", port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        self.player_id = self.connect()
        
    def connect(self):
        try:
            print(f"Attempting to connect to {self.server}:{self.port}")
            self.client.connect(self.addr)
            data = self.client.recv(2048)
            if not data:
                print("Received empty data during connection")
                return None
            return pickle.loads(data)
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            received_data = self.client.recv(2048)
            if not received_data:
                print("Received empty data from server")
                return None
                
            try:
                parsed_data = pickle.loads(received_data)
                return parsed_data
            except Exception as e:
                print(f"Error unpickling data: {e}")
                return None
        except socket.error as e:
            print(f"Socket Error: {e}")
            return None

    def disconnect(self):
        try:
            self.client.close()
        except:
            pass