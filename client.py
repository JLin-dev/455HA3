import socket
import threading
import sys

# Choose a Username
username = input('Input your username: ')

# Client Configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 5000         # Server's port number

# Initialize Client Socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Receive initial prompt from the server
def receive_initial_prompt():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'Username':
                client.send(username.encode('utf-8'))
                break
        except:
            print('An error occurred during the initial connection.')
            client.close()
            sys.exit()

# Receive Messages from Server
def receive_messages():
    while True:
        try:
            message = client.recv(1024)
            if not message:
                # Connection closed
                print('Connection closed by the server.')
                client.close()
                break
            if message.decode('utf-8').startswith('FILE'):
                # Handle file reception
                filename = message.decode('utf-8').split(' ', 1)[1]
                print(f'Receiving file "{filename}"...')
                receive_file(filename)
                print(f'File "{filename}" received.')
            else:
                message_decoded = message.decode('utf-8')
                if not message_decoded.startswith(f'{username}:'):
                    print(message_decoded)
        except:
            print('An error occurred!')
            client.close()
            break

# Send Messages to Server
def send_messages():
    while True:
        message_content = input('')
        if message_content == '/quit':
            client.close()
            print('You have disconnected from the chat.')
            break
        elif message_content.startswith('/send '):
            filename = message_content.split(' ', 1)[1]
            send_file(filename)
        else:
            message = f'{username}: {message_content}'
            client.send(message.encode('utf-8'))
            # Overwrite the input line with 'Me: [message_content]'
            sys.stdout.write('\033[F')
            sys.stdout.flush()
            sys.stdout.write('\033[K')
            sys.stdout.flush()
            print(f'Me: {message_content}')

# Function to Send Files
def send_file(filename):
    try:
        client.send(f'FILE {filename}'.encode('utf-8'))
        with open(filename, 'rb') as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                client.send(bytes_read)
        client.send('EOF'.encode('utf-8'))
        print(f'File "{filename}" has been sent.')
    except FileNotFoundError:
        print(f'File "{filename}" not found.')

# Function to Receive Files
def receive_file(filename):
    data = b''
    while True:
        bytes_read = client.recv(1024)
        if b'EOF' in bytes_read:
            # Split the data at 'EOF'
            data_parts = bytes_read.split(b'EOF')
            data += data_parts[0]
            break
        data += bytes_read
    with open(f'received_{filename}', 'wb') as f:
        f.write(data)

# Start the initial prompt handling
receive_initial_prompt()

# Start Threads for Receiving and Sending
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.start()
