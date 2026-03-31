import socket
import hashlib

def run_destino():
    ip = input("Digite o IP para escutar (ex: 127.0.0.1): ")
    porta = int(input("Digite a Porta: "))
    protocolo = input("Protocolo (TCP ou UDP): ").strip().upper()

    if protocolo == "TCP":
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, porta))
        server_socket.listen(1)
        print(f"Aguardando conexão TCP em {ip}:{porta}...")
        conn, addr = server_socket.accept()
        print(f"Conectado com {addr}")
    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((ip, porta))
        print(f"Aguardando pacotes UDP em {ip}:{porta}...")

    pacotes_recebidos = set()

    try:
        while True:
            if protocolo == "TCP":
                data = conn.recv(50)
                if not data: break
                addr_origem = None 
            else:
                data, addr_origem = server_socket.recvfrom(50)

            if len(data) == 50:
                id_pacote = int.from_bytes(data[:2], byteorder='big')
                checksum_recebido = data[2:10]
                payload = data[10:]
                
                checksum_calculado = hashlib.sha256(payload).digest()[:8]
                if checksum_recebido == checksum_calculado:
                    pacotes_recebidos.add(id_pacote)
                
                ack_packet = "ack".to_bytes(2, byteorder='big')
                if protocolo == "TCP":
                    conn.sendall(ack_packet)
                else:
                    server_socket.sendto(ack_packet, addr_origem)
                    
    except KeyboardInterrupt:
        print("\nEncerrando o Destino...")
    finally:
        if protocolo == "TCP": conn.close()
        server_socket.close()

if __name__ == "__main__":
    run_destino()
