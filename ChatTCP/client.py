import socket
import threading

nickname = input("Choose a nickname: ")

HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def receive():
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "NICK":
                client.send(nickname.encode(FORMAT))
                pass
            else:
                print(message)
        except:
            print("An error occurred")
            client.close()
            break


def send():
    connected = True

    while connected:
        user_input = input("")

        if user_input == DISCONNECT_MESSAGE:
            connected = False
            client.close()

        else:
            msg = f"{nickname}: {user_input}"
            message = msg.encode(FORMAT)
            msg_length = str(len(message)).encode(FORMAT)
            msg_length += b" " * (HEADER - len(msg_length))

        client.send(msg_length)
        client.send(message)


receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()

