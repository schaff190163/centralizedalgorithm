import socket
import threading

class CentralizedCoordinator:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request_queue = []
        self.shared_resource_lock = threading.Lock()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Coordinator listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        with client_socket:
            print(f"Connection established with {client_address}")

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                self.process_message(message, client_socket)

    def process_message(self, message, client_socket):
        if message == "REQUEST_ACCESS":
            self.handle_access_request(client_socket)

    def handle_access_request(self, client_socket):
        with self.shared_resource_lock:
            if not self.request_queue:
                client_socket.sendall("GRANTED".encode('utf-8'))
                print("Client was GRANTED!")
            else:
                self.request_queue.append(client_socket)
                client_socket.sendall("DENIED".encode('utf-8'))
                print("Client is in queue!")

if __name__ == "__main__":
    coordinator = CentralizedCoordinator('172.31.183.206', 8080)
    coordinator.start()
