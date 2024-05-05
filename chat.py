import sys
import re
import socket
import threading


connections = {}


# SERVER PART
def handle_user_connection(connection: socket.socket, address: str) -> None:
    while True:
        try:
            # get the message
            msg = connection.recv(1024)

            if msg:
                # log message on the server
                print(f'{address[0]}:{address[1]} - {msg.decode()}')

                broadcast(msg.decode(), connection)

            else:
                remove_connection(connection)
                break

        except Exception as e:
            print(f'Error to handle user connection: {e}')
            remove_connection(connection)
            break


def broadcast(message: str, connection: socket.socket) -> None:
    # check if this message is for a specific user
    if len(message) >= 3 and message[0:3] == 'to:':
        match = re.search(r"^to:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5} ", message)
        # print(match)
        if match is None:
            connection.send('SERVER: No such user or wrong format (must be \"to:ipaddress:port funny_message\")'.encode())
        else:
            addr, port = match.group(0).split(':')[1:3]

            direct_client = list(connections.keys())[list(connections.values()).index((addr, int(port)))]

            address = connections[connection]
            message_wo_destination = message.replace(match.group(0), '')
            msg_to_send = f'Direct message from {address[0]}:{address[1]} - {message_wo_destination}'
            direct_client.send(msg_to_send.encode())
    else:
        # else just broadcast
        address = connections[connection]
        msg_to_send = f'From {address[0]}:{address[1]} - {message}'

        # send to all clients
        for client_conn in connections.keys():
            if client_conn != connection:
                try:
                    client_conn.send(msg_to_send.encode())
                except Exception as e:
                    print('Error broadcasting message: {e}')
                    remove_connection(client_conn)


def remove_connection(conn: socket.socket) -> None:
    if conn in connections.keys():
        # close connection
        conn.close()
        connections.pop(conn)


def server(LISTENING_PORT: str) -> None:
    try:
        # set the limit by 4
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.bind(('', int(LISTENING_PORT)))
        socket_instance.listen(4)

        print('Server running!')

        while True:
            socket_connection, address = socket_instance.accept()
            # add client
            connections[socket_connection] = address
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)
        socket_instance.close()


# CLIENT PART
def handle_messages(connection: socket.socket):

    while True:
        try:
            msg = connection.recv(1024)

            if msg:
                print(msg.decode())
            else:
                connection.close()
                break

        except Exception as e:
            print(f'Error handling message from server: {e}')
            connection.close()
            break


def client(SERVER_ADDRESS: str, SERVER_PORT: str) -> None:
    try:
        # set up a connection
        socket_instance = socket.socket()
        socket_instance.connect((SERVER_ADDRESS, int(SERVER_PORT)))

        threading.Thread(target=handle_messages, args=[socket_instance]).start()

        print('Connected to chat!')

        while True:
            msg = input()
            if msg == 'quit' or msg == 'q':
                break
            socket_instance.send(msg.encode())

        socket_instance.close()
        return

    except Exception as e:
        print(f'Error connecting to server socket {e}')
        socket_instance.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('You need to specify the mode (server or client). For examples call help with -h.')
    elif sys.argv[1] == '-h':
        print('To run chat as a server you need to specify a port: python3 chat.py server 12000')
        print('To run chat as a client you need to specify an address and a port: '
              'python3 chat.py client 127.0.0.1 12000')
    else:
        if sys.argv[1] == 'server':
            if len(sys.argv) < 3:
                print('In server mode you need to specify a port to host on')
            else:
                server(sys.argv[2])
        elif sys.argv[1] == 'client':
            if len(sys.argv) < 4:
                print('In client mode you need to specify an address and a port of the server')
            else:
                client(sys.argv[2], sys.argv[3])
        else:
            print('Chat has only two modes: server and client')
