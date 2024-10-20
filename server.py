import socket
import threading

# Server Configuration
HOST = '127.0.0.1'  
PORT = 5000         

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.settimeout(1)  # Set timeout to allow graceful shutdown

clients = []
usernames = []

# Broadcast Message to All Connected Clients Except Sender
def broadcast(message, sender_client):
    for client in clients:
        if client != sender_client:
            try:
                client.send(message)
            except:
                # Handle broken client connections
                remove_client(client)

def remove_client(client):
    if client in clients:
        index = clients.index(client)
        client.close()
        username = usernames[index]
        broadcast(f'{username} has left the chat.'.encode('utf-8'), client)
        usernames.remove(username)
        clients.remove(client)
        print(f'{username} has disconnected.')

def forward_file(sender_client):
    while True:
        try:
            bytes_read = sender_client.recv(1024)
            if bytes_read == b'EOF':
                broadcast(bytes_read, sender_client)
                break
            broadcast(bytes_read, sender_client)
        except:
            remove_client(sender_client)
            break

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                remove_client(client)
                break
            elif message.decode('utf-8').startswith('FILE'):
                # Handle file transfer
                filename = message.decode('utf-8').split(' ', 1)[1]
                broadcast(message, client)
                forward_file(client)
            else:
                broadcast(message, client)
        except:
            remove_client(client)
            break

def receive_connections():
    while True:
        try:
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
        except socket.timeout:
            continue
        except OSError:
            # Socket has been closed
            break

print('Server is running...')

try:
    receive_connections()
except KeyboardInterrupt:
    print('\nShutting down the server...')
finally:
    for client in clients:
        client.close()
    server.close()
    print('Server has been shut down.')
