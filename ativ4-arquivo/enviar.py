import socket
import time
import hashlib
import os
import struct
import sys


pacotes_enviados = 0
retransmissoes = 0
acks_recebidos = 0
pacotes_perdidos = 0

TIMEOUT = 2.0
MAX_TENTATIVAS = 5


def calcular_hash_arquivo(caminho):
    """Calcula SHA-256 do arquivo inteiro."""
    sha = hashlib.sha256()
    with open(caminho, "rb") as f:
        while True:
            bloco = f.read(8192)
            if not bloco:
                break
            sha.update(bloco)
    return sha.hexdigest()


def enviar_metadados(nome_arquivo, tamanho, hash_arquivo, sock, protocolo, destino):

    dado = f"{nome_arquivo}@{tamanho}@{hash_arquivo}"
    payload = dado.encode("utf-8")
    # Adiciona checksum ao pacote de metadados
    checksum = hashlib.sha256(payload).digest()[:8]
    payload = payload + checksum

    ack_recebido = False
    tentativas = 0

    while not ack_recebido:
        try:
            if protocolo == "TCP":
                sock.sendall(payload)
            else:
                sock.sendto(payload, destino)

            sock.settimeout(TIMEOUT)
            ack_data = sock.recv(1024)

            if ack_data == b"ack":
                ack_recebido = True
                print("Metadados recebidos pelo destino.")

        except socket.timeout:
            tentativas += 1
            print(f"Timeout ao enviar metadados (tentativa {tentativas})")
            if tentativas > MAX_TENTATIVAS:
                print("Falha ao enviar metadados.")
                sys.exit(1)
        except Exception as e:
            tentativas += 1
            print(f"Erro: {e} (tentativa {tentativas})")
            if tentativas > MAX_TENTATIVAS:
                print("Falha ao enviar metadados.")
                sys.exit(1)


def enviar_pacote(chunk, chunk_number, sock, protocolo, destino):

    global pacotes_enviados, acks_recebidos, retransmissoes, pacotes_perdidos

    id_bytes = struct.pack(">I", chunk_number)  # 4 bytes big-endian
    corpo = id_bytes + chunk  # chunk já é bytes (lido em modo "rb")
    checksum = hashlib.sha256(corpo).digest()[:8]
    payload = corpo + checksum

    ack_recebido = False
    tentativas = 0

    while not ack_recebido:
        try:
            if protocolo == "TCP":
                # Envia tamanho do payload primeiro (4 bytes) + payload
                tamanho_payload = struct.pack(">I", len(payload))
                sock.sendall(tamanho_payload + payload)
            else:
                sock.sendto(payload, destino)

            pacotes_enviados += 1

            sock.settimeout(TIMEOUT)
            ack_data = sock.recv(1024)

            if ack_data == b"ack":
                ack_recebido = True
                acks_recebidos += 1

        except socket.timeout:
            retransmissoes += 1
            tentativas += 1
            print(
                f"  [PKT {chunk_number}] Timeout — retransmitindo (tentativa {tentativas})..."
            )
            if tentativas > MAX_TENTATIVAS:
                pacotes_perdidos += 1
                print(
                    f"  [PKT {chunk_number}] Pacote perdido após {MAX_TENTATIVAS} tentativas."
                )
                break
        except Exception as e:
            retransmissoes += 1
            tentativas += 1
            print(f"  [PKT {chunk_number}] Erro: {e}")
            if tentativas > MAX_TENTATIVAS:
                pacotes_perdidos += 1
                break


def enviar_arquivo(caminho, chunk_size, sock, protocolo, destino):

    with open(caminho, "rb") as f:
        chunk_number = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            enviar_pacote(chunk, chunk_number, sock, protocolo, destino)
            chunk_number += 1
            # Progresso
            if chunk_number % 50 == 0:
                print(f"{chunk_number} pacotes enviados")

    return chunk_number


def enviar_fim(sock, protocolo, destino):

    payload = b"__FIM__"
    checksum = hashlib.sha256(payload).digest()[:8]
    payload = payload + checksum

    ack_recebido = False
    tentativas = 0

    while not ack_recebido:
        try:
            if protocolo == "TCP":
                tamanho_payload = struct.pack(">I", len(payload))
                sock.sendall(tamanho_payload + payload)
            else:
                sock.sendto(payload, destino)

            sock.settimeout(TIMEOUT)
            ack_data = sock.recv(1024)

            if ack_data == b"ack":
                ack_recebido = True
                print("[FIM] Sinalização de fim confirmada pelo destino.")
        except socket.timeout:
            tentativas += 1
            if tentativas > MAX_TENTATIVAS:
                print("[FIM] Destino não confirmou fim. Encerrando mesmo assim.")
                break
        except Exception:
            tentativas += 1
            if tentativas > MAX_TENTATIVAS:
                break


def formatar_numero(valor, decimais=2):

    if isinstance(valor, int):
        parte_inteira = f"{valor:,}".replace(",", ".")
        return parte_inteira
    else:
        parte_inteira = int(valor)
        parte_decimal = round(valor - parte_inteira, decimais)
        inteiro_fmt = f"{parte_inteira:,}".replace(",", ".")
        decimal_fmt = f"{parte_decimal:.{decimais}f}"[2:]  # tira o "0."
        return f"{inteiro_fmt},{decimal_fmt}"


def exibir_relatorio(
    nome_arquivo, tamanho, chunk_size, total_pacotes, tempo_total, hash_arquivo
):

    bits_transmitidos = tamanho * 8
    velocidade_bps = bits_transmitidos / tempo_total if tempo_total > 0 else 0

    print("       RELATÓRIO DE TRANSMISSÃO — ORIGEM\n")
    print(f"  Arquivo ............: {nome_arquivo}")
    print(f"  Tamanho ............: {formatar_numero(tamanho)} bytes")
    print(f"  SHA-256 ............: {hash_arquivo[:32]}...")
    print(f"  Tamanho do bloco ...: {formatar_numero(chunk_size)} bytes")
    print(f"  Pacotes enviados ...: {formatar_numero(total_pacotes)}")
    print(f"  ACKs recebidos .....: {formatar_numero(acks_recebidos)}")
    print(f"  Retransmissões .....: {formatar_numero(retransmissoes)}")
    print(f"  Pacotes perdidos ...: {formatar_numero(pacotes_perdidos)}")
    print(f"  Tempo total ........: {formatar_numero(tempo_total, 4)} s")
    print(f"  Velocidade média ...: {formatar_numero(velocidade_bps)} bit/s")


def run_origem():
    global pacotes_enviados, retransmissoes, acks_recebidos, pacotes_perdidos

    # Reset estatísticas
    pacotes_enviados = 0
    retransmissoes = 0
    acks_recebidos = 0
    pacotes_perdidos = 0

    print("TRANSFERÊNCIA P2P — MODO (ENVIO)")

    ip_destino = input("IP de destino: ").strip()
    porta_destino = int(input("Porta de destino: "))
    protocolo = input("Protocolo (TCP ou UDP): ").strip().upper()

    while protocolo not in ("TCP", "UDP"):
        protocolo = input("Protocolo inválido. Digite TCP ou UDP: ").strip().upper()

    print("Tamanho do bloco (bytes):")
    print("  1) 500")
    print("  2) 1.000")
    print("  3) 1.500")
    opcao = input("Escolha (1/2/3): ").strip()
    chunk_map = {"1": 500, "2": 1000, "3": 1500}
    chunk_size = chunk_map.get(opcao, 1000)
    print(f"Bloco escolhido: {chunk_size} bytes")

    arquivo = input("Caminho do arquivo a enviar: ").strip()
    if not os.path.isfile(arquivo):
        print(f"Arquivo '{arquivo}' não encontrado.")
        return

    nome_arquivo = os.path.basename(arquivo)
    tamanho = os.path.getsize(arquivo)
    destino = (ip_destino, porta_destino)

    hash_arquivo = calcular_hash_arquivo(arquivo)
    print(f"Hash: {hash_arquivo}")

    # Criar socket
    if protocolo == "TCP":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(destino)
        destino_param = destino
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        destino_param = destino

    enviar_metadados(
        nome_arquivo, tamanho, hash_arquivo, sock, protocolo, destino_param
    )

    print("Iniciando transmissão do arquivo\n")
    inicio = time.time()

    total_pacotes = enviar_arquivo(arquivo, chunk_size, sock, protocolo, destino_param)

    # Sinalizar fim
    enviar_fim(sock, protocolo, destino_param)

    tempo_total = time.time() - inicio

    exibir_relatorio(
        nome_arquivo, tamanho, chunk_size, total_pacotes, tempo_total, hash_arquivo
    )

    sock.close()
    print("Conexão encerrada.")


if __name__ == "__main__":
    run_origem()
