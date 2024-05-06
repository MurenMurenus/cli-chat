import re
import threading
import socket

LISTENING_PORT = 5005


def handle_messages() -> None:
    try:
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_instance.bind(('', LISTENING_PORT))
    except Exception as e:
        print(f'Error binding listening socket: {e}')
        return

    while True:
        try:
            msg, addr = socket_instance.recvfrom(1024)

            msg_to_print = f'{addr[0]}: {msg.decode()}'
            if msg:
                print(msg_to_print)
            else:
                socket_instance.close()
                break

        except Exception as e:
            print(f'Error handling message from server: {e}')
            socket_instance.close()
            break


def send_message(msg: str) -> None:
    if len(msg) >= 3 and msg[0:3] == 'to:':
        # direct message
        match = re.search(r"^to:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", msg)
        # print(match)
        if match is None:
            print('Wrong format (must be \"to:ipaddress funny_message\")')
        else:
            addr = match.group(0).split(':')[1]
            msg_wo_destination = msg.replace(match.group(0), '')
            try:
                my_addr = socket.gethostbyname(socket.gethostname())
                # msg_to_send = f'{my_addr}: {msg_wo_destination}'
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(msg_wo_destination.encode(), (addr, LISTENING_PORT))
            except Exception as e:
                print(f'Error sending direct message: {e}')
                return

    else:
        # broadcast
        try:
            # print(f'HOSTNAME: {socket.gethostname()}')
            my_addr = socket.gethostbyname(socket.gethostname())
            # msg_to_send = f'{my_addr}: {msg}'
            # my_addr_broadcast = my_addr.split('.')
            # my_addr_broadcast[2] = '255'
            # my_addr_broadcast[3] = '255'
            # my_addr_broadcast = '.'.join(my_addr_broadcast)

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(msg.encode(), ('255.255.255.255', LISTENING_PORT))
        except Exception as e:
            print(f'Error while broadcasting: {e}')
            return


def client() -> None:
    try:
        threading.Thread(target=handle_messages).start()
        while True:
            msg = input()
            if msg == 'quit' or msg == 'q':
                break
            send_message(msg)

        return

    except Exception as e:
        print(f'Error occurred {e}')


if __name__ == "__main__":
    client()
