# socket_client.py
import socketio
sio = socketio.Client()
def connect_to_server():
    try:
        sio.connect('http://localhost:3009', wait=True, wait_timeout=5)
        print("Successfully connected to the server.")
    except Exception as e:
        print(f"Failed to connect: {e}")

def reconnect(max_retries=5, delay=5):
    import time
    attempts = 0
    while attempts < max_retries:
        try:
            sio.connect('http://localhost:3009', wait=True, wait_timeout=5)
            print("Reconnected to the server.")
            return
        except Exception as e:
            attempts += 1
            time.sleep(delay)
    print("Failed to reconnect after multiple attempts.")

@sio.event
def connect():
    print("Connected to the Socket.IO server.")

@sio.event
def disconnect():
    print("Disconnected from the Socket.IO server.")
    reconnect()

def send_socket(socket_type, data):
    """
    Emit a message to the Socket.IO server.
    """
    try:
        sio.emit(socket_type, data)
        print(f"Message sent: {socket_type} -> {data}")
    except Exception as e:
        print(f"Failed to send message: {e}")

connect_to_server()
