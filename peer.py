# importing necessary packages
import socket
import threading
import pickle
import random


def main():
    server_port = int(input('What port do you want to open server on?'))
    print(f'*********** Starting server thread on port {server_port} ***********')
    server_thread = threading.Thread(target=server, args=(server_port,))
    server_thread.start()
    send_msg = input('do you want to send a message?(y / n) ')
    if send_msg == 'y':
        msg = input('enter your message: ')
        local_port_number = int(input('enter local port number: '))
        server_port_number = int(input('enter destination server port: '))
        client_thread = threading.Thread(target=client,
                                         args=({'msg': msg, 'packet_number': random.randint(0, 1000)}, False,
                                               server_port_number, local_port_number))
        client_thread.start()


def client(msg, is_ack, dest_port, local_port=12347):  # 12347 is just a default value for local port
    # sending message as python dictionary and a random number for packet to check the ack later
    # I also added a flag named is_ack to tell the client if the message is a normal message or is a ack message
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    host = socket.gethostname()

    packet_number = msg['packet_number']
    # set the socket a default value if the message is normal unless use a random number
    # ack message's socket port number can't be the same as sending message socket because that socket is still open in another thread
    if not is_ack:
        s.bind((host, local_port))

    print(f'sending {msg} to {dest_port}')

    s.sendto(pickle.dumps(msg), (host, dest_port))  # pickle.dumps is for converting python dictionary to bytes
    if not is_ack:  # if the message is a normal message, wait for ack but if it's a ack message, just close socket
        s.settimeout(1)  # set a timeout for socket to send the packet again if it didn't receive ack
        data = None
        while not data:
            try:
                data, address = s.recvfrom(1024)
                received_data = pickle.loads(data)  # pickle.loads is for converting bytes to python dictionary
                if received_data['packet_number'] == packet_number:  # check the packet number in the ack equals the sending packet_number
                    print(f"ack received {received_data} from {address}")
                else:
                    data = None  # we want the while loop to continue
            except socket.timeout:
                print("didn't receive ack sending again")
                print(f'sending {msg} to {dest_port}')
                s.sendto(pickle.dumps(msg), (host, dest_port))

    s.close()


def server(local_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = socket.gethostname()

    s.bind((host, local_port))

    while True:
        data, address = s.recvfrom(1024)
        received_data = pickle.loads(data)
        print(f'received message {received_data}, {address}')
        ack_packet = {'msg': "ack", 'packet_number': received_data['packet_number']}
        # start a new thread for ack message with the client function and is_ack=True
        ack_thread = threading.Thread(target=client, args=(ack_packet, True, address[1]))
        ack_thread.start()


if __name__ == '__main__':
    main()
