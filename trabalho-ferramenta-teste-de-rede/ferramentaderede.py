import argparse
import socket
import time

TAMANHO_PAYLOAD = 500
STRING_BASE = "teste de rede 2026"
DURACAO = 20
DEFAULT_PORT = 5555

FIN_TRANSMISSAO = b"FIN"
TIMEOUT = 4.0


def montar_pacote(seq: int) -> bytes:

    cabecalho = f"{seq:010d}|{STRING_BASE}|".encode(
        "utf-8"
    )  # Adiciona zeros antes do valor de sequencia do pacote.
    enchimento = b"X" * (
        TAMANHO_PAYLOAD - len(cabecalho)
    )  # completa com os bytes restantes para dar 500 com X
    return cabecalho + enchimento


def montar_fin(total: int) -> bytes:

    cabecalho = f"FIN|{total:010d}|".encode("utf-8")  # para enviar fim de transmissão
    enchimento = b"X" * (TAMANHO_PAYLOAD - len(cabecalho))  # completa o pacote
    return cabecalho + enchimento


def eh_fin(pacote: bytes) -> bool:
    return (
        pacote[:3] == FIN_TRANSMISSAO
    )  # função auxiliar para verificar fim de transmissão


def extrair_total_fin(pacote: bytes) -> int:
    return int(pacote.split(b"|")[1])  # pegar total de pacotes


def extrair_seq(pacote: bytes) -> int:
    return int(pacote.split(b"|", 1)[0])


def fmt_milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")  # colocar o ponto como separador de milhar.


# Recebe total em bits por segundo -> retorna a velocidade em {Gbit/s,Mbit/s,Kbit/s ou bit/s}
def fmt_bitrate(bits_por_seg: float) -> str:

    if bits_por_seg >= 1e9:
        return f"{bits_por_seg / 1e9:.2f} Gbit/s"

    if bits_por_seg >= 1e6:
        return f"{bits_por_seg / 1e6:.2f} Mbit/s"

    if bits_por_seg >= 1e3:
        return f"{bits_por_seg / 1e3:.2f} Kbit/s"

    return f"{bits_por_seg:.2f} bit/s"


# Recebe: Protocolo, total de pacotes enviados, total de pacotes recebitos, total de bytes trafegados na transmissão e o tempo decorrido
# Printa: Os dados do relatorio
def imprimir_relatorio(proto, enviados, recebidos, bytes_traf, decorrido):

    perdidos = max(enviados - recebidos, 0)
    perda_pct = (perdidos / enviados * 100.0) if enviados else 0.0
    decorrido = max(decorrido, 1e-9)
    pps = recebidos / decorrido
    bps = (bytes_traf * 8) / decorrido

    print(f"RELATORIO DE DESEMPENHO - {proto.upper()}")
    print(f" Tempo de medicao: {decorrido:.2f} s")
    print(f" Pacotes enviados: {fmt_milhar(enviados)}")
    print(f" Pacotes recebidos: {fmt_milhar(recebidos)}")
    print(f" Pacotes perdidos: {fmt_milhar(perdidos)} ({perda_pct:.2f}%)")
    print(f" Bytes trafegados: {fmt_milhar(bytes_traf)}  bytes")
    print(f" Vazao (pacotes/s): {fmt_milhar(int(pps))} pps")
    print(f" Vazao (rede): {fmt_bitrate(bps)}")


# Lógica do sender


# Recebe: protocolo, host, porta, duracao da linha de comando.
# Funcionalidades:
# 1 - executa socket correto TCP ou UDP e realiza conexão com o destino
# 2 - inicia o temporizador da origem, e fica enviando pacotes até o fim dos 20 segundos
# 3 - envia o FIN ACK para aviso de fim de transmissão
def executar_sender(proto, host, port, duracao):
    if proto == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        destino = None

    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1 << 20)
        destino = (host, port)

    print(f"{proto.upper()} enviando para {host}:{port} por {duracao} s")

    seq = 0
    inicio = time.monotonic()
    fim = inicio + duracao

    while time.monotonic() < fim:
        pacote = montar_pacote(seq)

        if proto == "tcp":
            sock.sendall(pacote)
        else:
            try:
                sock.sendto(pacote, destino)
            except OSError:
                continue

        seq += 1
    decorrido = time.monotonic() - inicio

    # após o término dos 20 segundos envia-se o aviso de término

    fin = montar_fin(seq)

    if proto == "tcp":
        sock.sendall(fin)
        sock.shutdown(socket.SHUT_WR)
        time.sleep(0.2)
    else:
        for _ in range(5):  # tenta enviar o aviso 5 vezes
            sock.sendto(fin, destino)
            time.sleep(0.05)

    sock.close()  # fecha o socket
    pps = seq / decorrido if decorrido else 0

    print(
        f"{proto.upper()} finalizado: {fmt_milhar(seq)} pacotes em {decorrido:.2f}s ({fmt_milhar(int(pps))} pps de envio)"
    )


# Lógica do receptor


# Funcionalidade: confere protocolo e chama callback correspondente
def executar_receiver(proto, port, duracao):
    if proto == "tcp":
        _receiver_tcp(port)
    else:
        _receiver_udp(port)


def _receiver_tcp(port):

    # Inicia socket e aguarda conexão do sender

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(1)
    print(f"[TCP] aguardando conexao na porta {port}")
    conn, addr = srv.accept()
    print(f"[TCP] conectado por {addr[0]}:{addr[1]}")

    # inicializa variáveis de controle para relatório
    recebidos = 0
    bytes_traf = 0
    enviados_reportado = None
    buffer = b""
    inicio = None
    ultimo = None

    while True:
        dados = conn.recv(65536)
        if not dados:
            break
        if inicio is None:
            inicio = time.monotonic()  # incializa o timer
        buffer += dados
        terminou = False

        # TCP e um fluxo de bytes: refatiamos em quadros de 500 bytes
        while len(buffer) >= TAMANHO_PAYLOAD:
            quadro = buffer[:TAMANHO_PAYLOAD]  # peca um pacote do buffer
            buffer = buffer[TAMANHO_PAYLOAD:]
            if eh_fin(quadro):  # verifica se é um pacote final
                enviados_reportado = extrair_total_fin(quadro)
                terminou = True
                break
            recebidos += 1  # faz a lógica de quantidades de pacotes recebidos
            bytes_traf += TAMANHO_PAYLOAD
            ultimo = time.monotonic()
        if terminou:
            break

    conn.close()
    srv.close()
    decorrido = (ultimo - inicio) if (inicio and ultimo) else 0.0
    enviados = enviados_reportado if enviados_reportado is not None else recebidos
    imprimir_relatorio("tcp", enviados, recebidos, bytes_traf, decorrido)


def _receiver_udp(port):

    # inicia lógica do receptor UDP
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 21)
    srv.bind(("0.0.0.0", port))
    print(f"[UDP] aguardando pacotes na porta {port}")

    recebidos = 0
    bytes_traf = 0
    enviados_reportado = None
    max_seq = -1
    inicio = None
    ultimo = None
    srv.settimeout(None)  # bloqueia ate o primeiro pacote

    while True:
        try:
            dados, addr = srv.recvfrom(65536)
        except socket.timeout:
            break  # sender terminou e o FIN se perdeu
        if inicio is None:
            inicio = time.monotonic()
            srv.settimeout(TIMEOUT)
        if eh_fin(dados):
            enviados_reportado = extrair_total_fin(dados)
            break
        recebidos += 1
        bytes_traf += len(dados)
        ultimo = time.monotonic()
        try:
            s = extrair_seq(dados)
            if s > max_seq:
                max_seq = s
        except ValueError:
            pass

    srv.close()
    decorrido = (ultimo - inicio) if (inicio and ultimo) else 0.0
    if enviados_reportado is not None:
        enviados = enviados_reportado
    elif max_seq >= 0:
        enviados = max_seq + 1  # estimativa se o FIN sumiu
    else:
        enviados = recebidos
    imprimir_relatorio("udp", enviados, recebidos, bytes_traf, decorrido)


def main():

    p = argparse.ArgumentParser(description="Ferramenta de teste de desempenho de rede")
    p.add_argument(
        "papel", choices=["sender", "receiver"], help="papel desta maquina nesta rodada"
    )
    p.add_argument(
        "--proto", choices=["tcp", "udp"], required=True, help="protocolo de transporte"
    )
    p.add_argument(
        "--host", default="127.0.0.1", help="IP do receiver (usado apenas pelo sender)"
    )
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument(
        "--tempo",
        type=int,
        default=DURACAO,
        help="duracao do teste em segundos (padrao: 20)",
    )
    args = p.parse_args()

    if args.papel == "sender":
        executar_sender(args.proto, args.host, args.port, args.tempo)
    else:
        executar_receiver(args.proto, args.port, args.tempo)


if __name__ == "__main__":
    main()
