from re import split
import socket
import time
import hashlib
import os

# fazer menu para escolher quantidade de bytes a ser enviadaa
# mandar somente o sha256 do arquivo inicial completo e não a cada pacote
# fazer a lógica de ser receptor também, que vai ter que ser com menu também

protocolo = ""
pacotes_perdidos = 0
retransmissoes = 0
acks_recebidos = 0
pacotes_perdidos = 0
chunk_size = 1000


def enviar_metadados(arquivo, tamanho, socket):
    global protocolo
    dado = arquivo + "@" + str(tamanho)
    payload = dado.encode("utf-8")
    checksum = hashlib.sha256(payload).digest()[:8]
    payload = payload + checksum
    ack_recebido = False

    while not ack_recebido:
        try:
            if protocolo == "TCP":
                socket.sendall(payload)
            else:
                socket.sendto(payload)

            ack_data = socket.recv(3)

            if ack_data == b"ack":
                ack_recebido = True

        except Exception as e:
            print("erro")

    return


def enviar_pacote(chunk, chunk_number, socket):

    global \
        protocolo, \
        acks_recebidos, \
        dados_transmitidos, \
        retransmissoes, \
        pacotes_perdidos

    id_bytes = chunk_number.to_bytes(2, byteorder="big")
    payload = chunk.encode("uft-8")
    payload = id_bytes + payload
    checksum = hashlib.sha256(payload).digest()[:8]
    payload = payload + checksum
    ack_recebido = False
    tentativas = 0

    while not ack_recebido:
        try:
            if protocolo == "TCP":
                socket.sendall(payload)
            else:
                socket.sendto(payload)

            ack_data = socket.recv(3)
            print(f"data ack recebido: {ack_data}")
            if ack_data == b"ack":
                ack_recebido = True
                acks_recebidos += 1
        except Exception as e:
            retransmissoes += 1
            tentativas += 1
            if tentativas > 5:
                pacotes_perdidos += 1
                break


def split_file(arquivo, chunk_size, socket):

    with open(arquivo, "rb") as file:
        chunk_number = 0
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            enviar_pacote(chunk, chunk_number, socket)
            chunk_number += 1

    return chunk_number


def run_origem():

    global chunk_size

    ip_destino = input("IP de destino: ")
    porta_destino = int(input("Porta de destino: "))
    protocolo = input("Protocolo (TCP ou UDP): ").strip().upper()

    if protocolo == "TCP":
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_destino, porta_destino))
    else:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.connect((ip_destino, porta_destino))

    arquivo = "mapadacomputacao.png"
    info = os.stat(arquivo)
    tamanho = info.st_size

    enviar_metadados(arquivo, tamanho, client_socket)

    inicio_teste = time.time()

    quant_pacotes_enviados = split_file(arquivo, chunk_size, client_socket)

    tempo_total = time.time() - inicio_teste


if __name__ == "__main__":
    run_origem()
