import socket
import sys
import time
import subprocess
import hashlib

pacotes_enviados = 0
rodando = True
numero_pacote = 1
conteudo = "teste.redes.2026*" * 3
pacotes_retransmitidos = 0


def menu():

    print("Escolha o protocolo que deseja utilizar:")
    print("1 - TCP")
    print("2 - UDP")
    print("Escolha: ")
    protocolo = int(input())

    ip_destino = input("Digite o IP de destino")
    porta = int(input("Digite a porta de destino"))

    print("Selecione a quantidade de pacotes a ser enviados")
    print("1 - 10")
    print("2 - 100")
    print("3 - 1000")
    quantpacotes = int(input())

    match protocolo:
        case 1:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente_ack(ip_destino, porta, quantpacotes, cliente)

        case 2:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            cliente_ack(ip_destino, porta, quantpacotes, cliente)


def cliente_ack(ip_destino, porta, quantpacotes, socket):
    global numero_pacote, pacotes_enviados, conteudo, pacotes_retransmitidos
    tempo_inicio = time.perf_counter()

    conteude_encod = conteudo.encode("utf-8")[:40]

    try:
        socket.connect((ip_destino, porta))
        print(f"Conectado ao servidor {ip_destino}:{porta}")
    except Exception as e:
        print(f"Não foi possível conectar: {e}")

    while numero_pacote <= quantpacotes:
        id = numero_pacote.to_bytes(2, byteorder="big")
        payload = id + conteude_encod
        checksum = hashlib.sha256(payload).digest()[:8]
        payload = payload + checksum

        try:
            socket.send(payload)
            pacotes_enviados += 1
            time.sleep(2)
            ack = socket.recv(1024).decode("utf-8")
            if ack == "ACK":
                numero_pacote += 1
                break
            else:
                pacotes_retransmitidos += 1
                break

        except Exception as e:
            pass


def iniciarprotocolotcp(ip_destino, porta, quantpacotes):
    pass


# def iniciar_cliente():
#       global pacotes_enviados, pacotes_recebidos, rodando, numero_pacote
#
#       ip_destino = input("Digite o IP de destino")
#       porta = int(input("Digite a porta de destino: "))
#
#       cliente_tcp = socket.socket(
#           socket.AF_INET, socket.SOCK_STREAM
#       )  # af inet especifica que o ip é do tipo ipv4, sock_stream indica que estamos usando tcp
#
#       cliente_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#       try:
#           cliente_tcp.connect((ip_destino, porta))  # conecta ao servidor aws
#           print(f"[SUCESSO] Conectado ao servidor {ip_destino}:{porta}!")
#       except Exception as e:
#           print(f"[ERRO] Não foi possível conectar: {e}")
#           return
#
#
#       while rodando:
#           try:
#               sys.stdout.write("Você: ")
#               sys.stdout.flush()
#               mensagem = input()
#
#               if mensagem.lower() == "/sair":
#                   rodando = False
#                   break
#
#               if mensagem and rodando:
#                   cliente_tcp.send(mensagem.encode("utf-8"))
#                   pacotes_enviados += 1  # Contabiliza envio
#           except:
#               break
#       cliente_tcp.close()
#
#       print("\n" + "=" * 40)
#       print("  RESUMO DA SESSÃO (CONTABILIZAÇÃO) ")
#       print("=" * 40)
#       print(f"-> Pacotes (Mensagens) Enviados : {pacotes_enviados}")
#       print(f"-> Pacotes (Mensagens) Recebidos: {pacotes_recebidos}")
#       print("=" * 40)
#       print("Chat encerrado com sucesso.")
#       sys.exit(0)
#
#


if __name__ == "__main__":
    menu()
