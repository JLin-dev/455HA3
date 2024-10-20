import sys
import socket
import threading


username = input('Input your username:')

# Client Configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 5000         # Server's port number

# Initialize Client Socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Receive Messages from Server
def receive_messages():
    while True:
        try:
            message = client.recv(1024)
            if message.decode('utf-8').startswith('FILE'):
                # Start receiving the file
                filename = message.decode('utf-8').split(' ', 1)[1]
                print(f'Receiving file "{filename}"...')
                receive_file(filename)
                print(f'File "{filename}" received.')
            elif message.decode('utf-8') == 'Username':
                client.send(username.encode('utf-8'))
            else:
                message_decoded = message.decode('utf-8')
                if not message_decoded.startswith(f'{username}:'):
                    print(message_decoded)
        except:
            print('An error occurred!')
            client.close()
            break

def send_messages():
    while True:
        message_content = input('')
        if message_content.startswith('/send '):
            # Extract the filename from the command
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


def send_file(filename):
    try:
        # Send the initial message indicating a file transfer
        client.send(f'FILE {filename}'.encode('utf-8'))
        with open(filename, 'rb') as f:
            while True:
                # Read the file in chunks
                bytes_read = f.read(1024)
                if not bytes_read:
                    # File transmission is done
                    break
                client.send(bytes_read)
        # Send an EOF message to signal the end of the file
        client.send('EOF'.encode('utf-8'))
        print(f'File "{filename}" has been sent.')
    except FileNotFoundError:
        print(f'File "{filename}" not found.')

def receive_file(filename):
    with open(f'received_{filename}', 'wb') as f:
        while True:
            bytes_read = client.recv(1024)
            if bytes_read == b'EOF':
                # End of file transmission
                break
            f.write(bytes_read)


# Start Threads for Receiving and Sending
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.start()
