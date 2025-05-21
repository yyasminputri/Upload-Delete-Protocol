from socket import socket, AF_INET, SOCK_STREAM
import base64

def send_request(command):
    server_address = ('localhost', 45000)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(server_address)

    try:
        client_socket.sendall(f"{command}\r\n".encode('utf-8'))
        response = client_socket.recv(4096)
        print("Received:", response.decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    while True:
        command = input("Enter command (LIST, GET, IMAGE, UPLOAD, DELETE, QUIT): ").strip()
        if command == "LIST" or command == "IMAGE" or command.startswith("GET") or command.startswith("DELETE"):
            send_request(command)
        elif command.startswith("UPLOAD"):
            filename = input("Enter the filename to upload: ").strip()
            with open(filename, 'rb') as file:
                filecontent = base64.b64encode(file.read()).decode('utf-8')
            send_request(f"UPLOAD {filename} {filecontent}")
        elif command == "QUIT":
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()