import socket
import time

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to the coordinator.")

    def send_message(self, message):
        self.client_socket.sendall(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        return response

    def request_access(self):
        message = "REQUEST_ACCESS"
        response = self.send_message(message)
        print(f"Response from coordinator: {response}")

        if response == "GRANTED":
            print("Executing the example task (sleep for 20 seconds)...")
            time.sleep(20)

    def release(self):
        message = "RELEASE"
        response = self.send_message(message)
        print(f"Response from coordinator: {response}")

    def close(self):
        self.client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    client = Client('localhost', 8080)

    try:
        client.connect()

        # Example: Request access and perform a task (sleep for 20 seconds)
        client.request_access()

        # Example: Release access
        client.release()

    finally:
        client.close()
