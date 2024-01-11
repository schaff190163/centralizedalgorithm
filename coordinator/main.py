import socket
import threading
import queue

class CentralizedCoordinator:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request_queue = queue.Queue()
        self.shared_resource_lock = threading.Lock()
        self.client_id_counter = 1
        self.client_id_map = {}

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Coordinator listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            client_id = self.assign_client_id(client_socket)
            print(f"Connection established with {client_address}, Client ID: {client_id}")

            self.handle_client(client_socket, client_id)

    def assign_client_id(self, client_socket):
        with self.shared_resource_lock:
            client_id = self.client_id_counter
            self.client_id_counter += 1
            self.client_id_map[client_id] = client_socket
            return client_id

    def handle_client(self, client_socket, client_id):
        with client_socket:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                self.process_message(message, client_socket, client_id)

    def process_message(self, message, client_socket, client_id):
        if message == "REQUEST_ACCESS":
            self.handle_access_request(client_socket, client_id)
        if message == "RELEASE":
            self.handle_release(client_socket, client_id)

    def handle_access_request(self, client_socket, client_id):
        with self.shared_resource_lock:
            if not self.request_queue.empty():
                self.request_queue.put((client_socket, client_id))
                print(f"Client ID {client_id} added to the queue.")
                client_socket.sendall("ACCESS_DENIED".encode('utf-8'))
            else:
                client_socket.sendall(f"ACCESS_GRANTED, Your ID: {client_id}".encode('utf-8'))

    def handle_release(self, client_socket, client_id):
        with self.shared_resource_lock:
            if not self.request_queue.empty():
                next_client, next_client_id = self.request_queue.get()
                next_client.sendall(f"ACCESS_GRANTED, Your ID: {next_client_id}".encode('utf-8'))
            else:
                print("No clients waiting for access.")

if __name__ == "__main__":
    coordinator = CentralizedCoordinator('', 8080)
    coordinator.start()
