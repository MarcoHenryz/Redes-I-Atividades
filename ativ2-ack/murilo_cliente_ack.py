import socket
import string
import time
import hashlib


def criar_pacote(numero_pacote):

    id_bytes = numero_pacote.to_bytes(2, byteorder="big")
    conteudo = "teste.redes.2026*" * 3
    payload = conteudo.encode("utf-8")[:40]
    payload = id_bytes + payload
    checksum = hashlib.sha256(payload).digest()[:8]
    return id_bytes + payload + checksum


def run_origem():
    ip_destino = input("IP de destino: ")
    porta_destino = int(input("Porta de destino: "))
    protocolo = input("Protocolo (TCP ou UDP): ").strip().upper()
    qtd_testes = int(input("Bateria de testes (10, 100 ou 1000): "))
    timeout_segundos = 0.5

    if protocolo == "TCP":
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_destino, porta_destino))
    else:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_socket.settimeout(timeout_segundos)

    pacotes_perdidos = 0
    retransmissoes = 0
    acks_recebidos = 0
    dados_transmitidos = 0

    inicio_teste = time.time()

    for seq_num in range(1, qtd_testes + 1):
        pacote = criar_pacote(seq_num)
        dados_transmitidos += 1
        ack_recebido = False
        tentativas = 0

        while not ack_recebido:
            try:
                if protocolo == "TCP":
                    client_socket.sendall(pacote)
                else:
                    client_socket.sendto(pacote, (ip_destino, porta_destino))

                ack_data = client_socket.recv(2)
                ack_id = string.from_bytes(ack_data, byteorder="big")

                if ack_id == "ack":
                    ack_recebido = True
                    acks_recebidos += 1
            except socket.timeout:
                retransmissoes += 1
                tentativas += 1
                if tentativas > 5:
                    pacotes_perdidos += 1
                    break

    tempo_total = time.time() - inicio_teste

    total_trafegado = dados_transmitidos + retransmissoes + acks_recebidos

    print("\n=== ANÁLISE DE DESEMPENHO E DOCUMENTAÇÃO ===")
    print(f"Protocolo: {protocolo} | Bateria: {qtd_testes} pacotes")
    print(f"Pacotes Perdidos (Dropados): {pacotes_perdidos}")
    print(f"Retransmissões Realizadas: {retransmissoes}")
    print(f"Tempo Total de Execução: {tempo_total:.4f} segundos")
    print(f"Contabilidade Final (Total Trafegado): {total_trafegado} pacotes")

    client_socket.close()


if __name__ == "__main__":
    run_origem()
