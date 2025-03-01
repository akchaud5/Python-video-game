import socket
import pickle
import sys
import os
import traceback
import time

# Create debug log file
DEBUG_MODE = True
DEBUG_LOG_PATH = os.path.join(os.path.dirname(__file__), "network_debug.log")

def log(message):
    """Log a message to both console and log file"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    
    if DEBUG_MODE:
        try:
            with open(DEBUG_LOG_PATH, "a") as f:
                f.write(formatted + "\n")
        except:
            pass  # If logging fails, continue anyway

class Network:
    def __init__(self, server="localhost", port=5555):
        log(f"Network initialization with server={server}, port={port}")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        
        # Set a socket timeout of 10 seconds
        self.client.settimeout(10)
        log("Socket created with 10 second timeout")
        
        # Try to clear any existing log file
        if DEBUG_MODE:
            try:
                with open(DEBUG_LOG_PATH, "w") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Network debug log started\n")
            except:
                pass
                
        self.player_id = self.connect()
        
    def connect(self):
        """Attempt to connect to the server and get player ID"""
        try:
            # Debug connection information
            log(f"Attempting to connect to {self.server}:{self.port}")
            log(f"Socket details: {self.client}")
            
            # Get all possible IP addresses for the server
            try:
                all_ips = socket.gethostbyname_ex(self.server)
                log(f"Resolved server IPs: {all_ips}")
            except Exception as e:
                log(f"Could not resolve server IPs: {e}")
            
            # Try connection with increased timeout
            self.client.settimeout(30)  # 30-second timeout for connection
            log(f"Attempting to connect to {self.addr} with 30-second timeout")
            self.client.connect(self.addr)
            log("Connection established")
            
            # Wait for initial data
            log("Waiting for initial data from server...")
            data = self.client.recv(2048)
            
            if not data:
                log("ERROR: Received empty data during connection")
                return None
                
            # Try to unpickle the player ID
            log(f"Received {len(data)} bytes of data")
            try:
                player_id = pickle.loads(data)
                log(f"Successfully unpickled data: player_id = {player_id}")
                return player_id
            except Exception as e:
                log(f"ERROR: Failed to unpickle data: {e}")
                log(f"First 100 bytes of raw data: {data[:100]}")
                return None
                
        except socket.timeout:
            log("ERROR: Connection attempt timed out")
            return None
        except ConnectionRefusedError:
            log("ERROR: Connection refused - server may not be running or wrong IP/port")
            return None
        except Exception as e:
            log(f"ERROR: Unexpected connection error: {e}")
            log(traceback.format_exc())
            return None

    def send(self, data):
        """Send data to server and get response"""
        if not hasattr(self, 'client') or self.client is None:
            log("ERROR: Cannot send data - client socket is not initialized")
            return None
            
        try:
            log(f"Sending data to server: {data}")
            pickled_data = pickle.dumps(data)
            log(f"Pickled data size: {len(pickled_data)} bytes")
            
            self.client.send(pickled_data)
            log("Data sent, waiting for response...")
            
            received_data = self.client.recv(2048)
            if not received_data:
                log("ERROR: Received empty data from server")
                return None
                
            log(f"Received {len(received_data)} bytes from server")
            
            try:
                parsed_data = pickle.loads(received_data)
                log("Successfully unpickled server response")
                return parsed_data
            except Exception as e:
                log(f"ERROR: Error unpickling data: {e}")
                log(f"First 100 bytes of raw response: {received_data[:100]}")
                return None
                
        except socket.timeout:
            log("ERROR: Socket timeout while sending/receiving data")
            return None
        except socket.error as e:
            log(f"ERROR: Socket error: {e}")
            return None
        except Exception as e:
            log(f"ERROR: Unexpected error during send/receive: {e}")
            log(traceback.format_exc())
            return None

    def disconnect(self):
        """Close the connection"""
        try:
            log("Disconnecting from server")
            self.client.close()
            log("Disconnected")
        except Exception as e:
            log(f"ERROR: Error during disconnect: {e}")
            pass