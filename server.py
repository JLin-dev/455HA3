import socket
import threading

# Server Configuration
HOST = '127.0.0.1'  # Localhost
PORT = 5000         # Non-privileged port

# Initialize Server Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Lists to keep track of clients and their usernames
clients = []
usernames = []

# Broadcast Message to All Connected Clients Except Sender
def broadcast(message, sender_client):
    for client in clients:
        if client != sender_client:
            client.send(message)

# Forward File Data to All Clients Except Sender
def forward_file(sender_client):
    while True:
        bytes_read = sender_client.recv(1024)
        if bytes_read == b'EOF':
            broadcast(bytes_read, sender_client)
            break
        broadcast(bytes_read, sender_client)

# Handle Individual Client Connections
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if message.decode('utf-8').startswith('FILE'):
                filename = message.decode('utf-8').split(' ', 1)[1]
                broadcast(message, client)  # Notify other clients
                forward_file(client)
            else:
                broadcast(message, client)
        except:
            index = clients.index(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} left the chat.'.encode('utf-8'), client)
            usernames.remove(username)
            clients.remove(client)
            break

# Accept New Connections
def receive_connections():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        # Request and Store Username
        client.send('Username'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        # Announce New Connection
        print(f'Username of the client is {username}')
        broadcast(f'{username} joined the chat!'.encode('utf-8'), client)
        client.send('Connected to the server.'.encode('utf-8'))

        # Start Handling Thread for Client
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print('Server is running...')
receive_connections()
