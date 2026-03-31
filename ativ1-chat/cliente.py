import socket
import threading
import sys

pacotes_enviados = 0
pacotes_recebidos = 0
rodando = True


def receber_mensagens(sock):
    global pacotes_recebidos, rodando
    while rodando:
        try:
            mensagem = sock.recv(1024).decode(
                "utf-8"
            )  # recebe mensagens e decodifica de bytes para strings
            if mensagem:
                sys.stdout.write(f"\r[Outro Usuário]: {mensagem}\nVocê: ")
                sys.stdout.flush()
                pacotes_recebidos += 1
            else:
                print("\n[AVISO] Servidor encerrou a conexão.")
                rodando = False
                break
        except:
            if rodando:
                print("\n[AVISO] Conexão perdida.")
            rodando = False
            break


def iniciar_cliente():
    global pacotes_enviados, pacotes_recebidos, rodando

    print("=== BEM-VINDO AO CHAT TCP ===")
    ip_destino = input("Digite o IP de destino (IP do Servidor AWS): ")
    porta = int(input("Digite a porta TCP de destino: "))

    cliente = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    )  # af inet especifica que o ip é do tipo ipv4, sock_stream indica que estamos usando tcp

    try:
        cliente.connect((ip_destino, porta))  # conecta ao servidor aws
        print(f"[SUCESSO] Conectado ao servidor {ip_destino}:{porta}!")
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar: {e}")
        return

    thread_recebimento = threading.Thread(target=receber_mensagens, args=(cliente,))
    thread_recebimento.start()

    print(
        "Chat iniciado! Digite sua mensagem e aperte ENTER. Para fechar, digite '/sair'.\n"
    )

    while rodando:
        try:
            sys.stdout.write("Você: ")
            sys.stdout.flush()
            mensagem = input()

            if mensagem.lower() == "/sair":
                rodando = False
                break

            if mensagem and rodando:
                cliente.send(mensagem.encode("utf-8"))
                pacotes_enviados += 1  # Contabiliza envio
        except:
            break
    cliente.close()

    print("\n" + "=" * 40)
    print("  RESUMO DA SESSÃO (CONTABILIZAÇÃO) ")
    print("=" * 40)
    print(f"-> Pacotes (Mensagens) Enviados : {pacotes_enviados}")
    print(f"-> Pacotes (Mensagens) Recebidos: {pacotes_recebidos}")
    print("=" * 40)
    print("Chat encerrado com sucesso.")
    sys.exit(0)


if __name__ == "__main__":
    iniciar_cliente()
