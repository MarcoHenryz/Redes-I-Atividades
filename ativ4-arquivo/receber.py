import socket
import time
import hashlib
import os
import struct
import sys

# Estatísticas
pacotes_recebidos = 0
pacotes_gravados = 0
pacotes_duplicados = 0


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


# ===================== TCP helpers =====================
# Mesmo framing do enviar.py:
#   [4 bytes: tamanho do payload] [payload]


def tcp_enviar(sock, payload):
    header = struct.pack(">I", len(payload))
    sock.sendall(header + payload)


def tcp_receber(sock):
    header = _receber_exato(sock, 4)
    if not header:
        return None
    tamanho = struct.unpack(">I", header)[0]
    return _receber_exato(sock, tamanho)


def _receber_exato(sock, n):
    partes = []
    recebido = 0
    while recebido < n:
        parte = sock.recv(n - recebido)
        if not parte:
            return None
        partes.append(parte)
        recebido += len(parte)
    return b"".join(partes)


# ==============================================================


def receber_metadados(sock, protocolo):

    if protocolo == "TCP":
        data = tcp_receber(sock)
        addr = None
    else:
        data, addr = sock.recvfrom(4096)

    if not data or len(data) < 9:
        print("Pacote de metadados muito curto.")
        return None, None, None, addr

    payload = data[:-8]
    checksum_recebido = data[-8:]
    checksum_calculado = hashlib.sha256(payload).digest()[:8]

    if checksum_recebido != checksum_calculado:
        print("Checksum dos metadados inválido!")
        return None, None, None, addr

    texto = payload.decode("utf-8")
    partes = texto.split("@")
    if len(partes) != 3:
        print(f"Formato inesperado: {texto}")
        return None, None, None, addr

    nome_arquivo = partes[0]
    tamanho = int(partes[1])
    hash_origem = partes[2]

    # Enviar ACK
    if protocolo == "TCP":
        tcp_enviar(sock, b"ack")
    else:
        sock.sendto(b"ack", addr)

    return nome_arquivo, tamanho, hash_origem, addr


def receber_pacote_tcp(conn):

    data = tcp_receber(conn)
    if not data:
        return -1, None

    # Separar checksum
    corpo = data[:-8]
    checksum_recebido = data[-8:]

    # Verificar se é sinalização de FIM
    if corpo == b"__FIM__":
        checksum_calculado = hashlib.sha256(corpo).digest()[:8]
        if checksum_recebido == checksum_calculado:
            tcp_enviar(conn, b"ack")
            return None, None
        else:
            return -1, None

    # Verificar checksum
    checksum_calculado = hashlib.sha256(corpo).digest()[:8]
    if checksum_recebido != checksum_calculado:
        print("Checksum inválido — descartando pacote.")
        return -1, None

    # Extrair id e dados
    chunk_number = struct.unpack(">I", corpo[:4])[0]
    dados = corpo[4:]

    # Enviar ACK
    tcp_enviar(conn, b"ack")

    return chunk_number, dados


def receber_pacote_udp(sock):

    data, addr = sock.recvfrom(65535)

    corpo = data[:-8]
    checksum_recebido = data[-8:]

    # Verificar se é FIM
    if corpo == b"__FIM__":
        checksum_calculado = hashlib.sha256(corpo).digest()[:8]
        if checksum_recebido == checksum_calculado:
            sock.sendto(b"ack", addr)
            return None, None, addr
        else:
            return -1, None, addr

    # Verificar checksum
    checksum_calculado = hashlib.sha256(corpo).digest()[:8]
    if checksum_recebido != checksum_calculado:
        print("Checksum inválido — descartando pacote.")
        return -1, None, addr

    chunk_number = struct.unpack(">I", corpo[:4])[0]
    dados = corpo[4:]

    # Enviar ACK
    sock.sendto(b"ack", addr)

    return chunk_number, dados, addr


def formatar_numero(valor, decimais=2):

    if isinstance(valor, int):
        parte_inteira = f"{valor:,}".replace(",", ".")
        return parte_inteira
    else:
        parte_inteira = int(valor)
        parte_decimal = round(valor - parte_inteira, decimais)
        inteiro_fmt = f"{parte_inteira:,}".replace(",", ".")
        decimal_fmt = f"{parte_decimal:.{decimais}f}"[2:]
        return f"{inteiro_fmt},{decimal_fmt}"


def exibir_relatorio(
    nome_arquivo, tamanho, chunk_size, tempo_total, hash_origem, hash_destino
):
    """Exibe relatório formatado no terminal."""
    bits_recebidos = tamanho * 8
    velocidade_bps = bits_recebidos / tempo_total if tempo_total > 0 else 0
    integridade_ok = hash_origem == hash_destino

    print("      RELATÓRIO DE RECEPÇÃO — DESTINO\n")
    print(f"  Arquivo ............: {nome_arquivo}")
    print(f"  Tamanho ............: {formatar_numero(tamanho)} bytes")
    print(f"  Tamanho do bloco ...: {formatar_numero(chunk_size)} bytes")
    print(f"  Pacotes recebidos ..: {formatar_numero(pacotes_recebidos)}")
    print(f"  Pacotes gravados ...: {formatar_numero(pacotes_gravados)}")
    print(f"  Pacotes duplicados .: {formatar_numero(pacotes_duplicados)}")
    print(f"  Tempo total ........: {formatar_numero(tempo_total, 4)} s")
    print(f"  Velocidade média ...: {formatar_numero(velocidade_bps)} bit/s")
    print(f"  Hash Origem (SHA-256): {hash_origem[:32]}...")
    print(f"  Hash Destino (SHA-256): {hash_destino[:32]}...")
    if integridade_ok:
        print("ARQUIVO ÍNTEGRO (hashes coincidem)")
    else:
        print("ARQUIVO CORROMPIDO (hashes diferentes)")


def run_destino():
    global pacotes_recebidos, pacotes_gravados, pacotes_duplicados

    # Reset estatísticas
    pacotes_recebidos = 0
    pacotes_gravados = 0
    pacotes_duplicados = 0

    print("  TRANSFERÊNCIA P2P — MODO DESTINO (RECEPÇÃO)")

    porta = int(input("Porta para escutar: "))
    protocolo = input("Protocolo (TCP ou UDP): ").strip().upper()

    while protocolo not in ("TCP", "UDP"):
        protocolo = input("Protocolo inválido. Digite TCP ou UDP: ").strip().upper()

    print("Tamanho do bloco esperado (bytes):")
    print("  1) 500")
    print("  2) 1.000")
    print("  3) 1.500")
    opcao = input("Escolha (1/2/3): ").strip()
    chunk_map = {"1": 500, "2": 1000, "3": 1500}
    chunk_size = chunk_map.get(opcao, 1000)

    # Diretório de saída
    pasta_saida = "recebidos"
    os.makedirs(pasta_saida, exist_ok=True)

    if protocolo == "TCP":
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", porta))
        server_sock.listen(1)
        print(f"\nAguardando conexão na porta {porta}")
        conn, addr_origem = server_sock.accept()
        print(f" Conexão estabelecida com {addr_origem}")

        # Receber metadados
        nome_arquivo, tamanho, hash_origem, _ = receber_metadados(conn, protocolo)
        if nome_arquivo is None:
            print("Falha ao receber metadados.")
            conn.close()
            server_sock.close()
            return

        print(f"\n  Arquivo: {nome_arquivo}")
        print(f"  Tamanho: {formatar_numero(tamanho)} bytes")
        print(f"  Hash origem: {hash_origem[:32]}")
        print("\nRecebendo dados\n")

        caminho_saida = os.path.join(pasta_saida, nome_arquivo)
        pacotes_escritos = set()

        inicio = time.time()

        with open(caminho_saida, "wb") as f:
            while True:
                chunk_number, dados = receber_pacote_tcp(conn)

                if chunk_number is None:
                    # FIM recebido
                    print("\nSinalização de fim recebida.")
                    break

                if chunk_number == -1:
                    # Erro — ignorar
                    continue

                pacotes_recebidos += 1

                if chunk_number in pacotes_escritos:
                    pacotes_duplicados += 1
                    continue

                # Escrever na posição correta
                f.seek(chunk_number * chunk_size)
                f.write(dados)
                pacotes_escritos.add(chunk_number)
                pacotes_gravados += 1

                if pacotes_gravados % 50 == 0:
                    print(f"{pacotes_gravados} pacotes gravados")

        tempo_total = time.time() - inicio
        conn.close()
        server_sock.close()

    else:
        # UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", porta))
        print(f"\n[UDP] Escutando na porta {porta}")

        # Receber metadados
        nome_arquivo, tamanho, hash_origem, addr_origem = receber_metadados(
            sock, protocolo
        )
        if nome_arquivo is None:
            print("Falha ao receber metadados.")
            sock.close()
            return

        print(f"\n  Arquivo: {nome_arquivo}")
        print(f"  Tamanho: {formatar_numero(tamanho)} bytes")
        print(f"  Hash origem: {hash_origem[:32]}")
        print("\nRecebendo dados\n")

        caminho_saida = os.path.join(pasta_saida, nome_arquivo)
        pacotes_escritos = set()

        inicio = time.time()

        with open(caminho_saida, "wb") as f:
            while True:
                chunk_number, dados, addr = receber_pacote_udp(sock)

                if chunk_number is None:
                    print("\nSinalização de fim recebida.")
                    break

                if chunk_number == -1:
                    continue

                pacotes_recebidos += 1

                if chunk_number in pacotes_escritos:
                    pacotes_duplicados += 1
                    continue

                f.seek(chunk_number * chunk_size)
                f.write(dados)
                pacotes_escritos.add(chunk_number)
                pacotes_gravados += 1

                if pacotes_gravados % 50 == 0:
                    print(f"{pacotes_gravados} pacotes gravados")

        tempo_total = time.time() - inicio
        sock.close()

    # Calcular hash do arquivo recebido
    print("\nCalculando hash SHA-256 do arquivo recebido")
    hash_destino = calcular_hash_arquivo(caminho_saida)

    exibir_relatorio(
        nome_arquivo, tamanho, chunk_size, tempo_total, hash_origem, hash_destino
    )

    print(f"Arquivo salvo em: {caminho_saida}")


if __name__ == "__main__":
    run_destino()

