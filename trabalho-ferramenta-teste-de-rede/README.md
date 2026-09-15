# Ferramenta de Teste de Rede — Guia de Execução

Script Python (`ferramentaderede.py`) que mede vazão/perda entre duas máquinas usando TCP ou UDP. Uma máquina roda como `receiver`, a outra como `sender`. Este guia cobre todas as formas de conectar as duas máquinas, tanto por **cabo Ethernet** quanto por **Wi-Fi**.

## Uso básico do script

Receiver (roda primeiro):
```
python ferramentaderede.py receiver --proto udp --port 5555
```

Sender (roda depois, apontando pro IP do receiver):
```
python ferramentaderede.py sender --proto udp --host <IP_DO_RECEIVER> --port 5555
```

Trocar `udp` por `tcp` pra testar o outro protocolo. Use `--tempo` pra mudar a duração (padrão 20s).

As duas máquinas só conseguem se enxergar se estiverem na mesma sub-rede IP e com a porta liberada no firewall — as seções abaixo mostram como garantir isso em cada cenário.

---

## Conexão via cabo Ethernet (ponta a ponta, sem roteador)

Sem roteador/switch com DHCP no meio, nenhuma das duas pontas recebe IP automaticamente por padrão. Três formas de resolver:

### Opção 1 — IP estático manual (mais confiável, recomendada)

Definir IP fixo manualmente nas duas interfaces, mesma sub-rede.

**Linux (NetworkManager):**
```
# Máquina A (vai ser o receiver)
sudo nmcli con mod <nome-da-conexao> ipv4.addresses 192.168.50.1/24 ipv4.method manual
sudo nmcli con up <nome-da-conexao>

# Máquina B (vai ser o sender)
sudo nmcli con mod <nome-da-conexao> ipv4.addresses 192.168.50.2/24 ipv4.method manual
sudo nmcli con up <nome-da-conexao>
```
Descobrir o nome da conexão da interface do cabo com `nmcli con show`.

**Linux (sem NetworkManager, via `ip`):**
```
sudo ip addr add 192.168.50.1/24 dev eth0   # na máquina A
sudo ip addr add 192.168.50.2/24 dev eth0   # na máquina B
sudo ip link set eth0 up
```

**Windows:** Painel de Controle → Central de Rede → Alterar config do adaptador → propriedades do adaptador Ethernet → IPv4 → definir IP manual (ex: `192.168.50.1` / máscara `255.255.255.0`) em cada máquina.

Testar antes de rodar o script: `ping 192.168.50.2` (da A pra B).

### Opção 2 — Compartilhamento de conexão (ICS / "Shared to other computers")

Uma das máquinas vira um mini-DHCP pra outra, sem precisar digitar IP fixo em nenhuma das duas.

**Linux (NetworkManager):** na máquina que vai compartilhar, editar o método IPv4 da interface do cabo pra "Compartilhada com outros computadores" (Shared):
```
sudo nmcli con mod <nome-da-conexao> ipv4.method shared
sudo nmcli con up <nome-da-conexao>
```
A outra máquina recebe IP via DHCP automaticamente (geralmente faixa `10.42.0.x`). Descobrir o IP dela com `ip a` ou `hostname -I` e usar esse IP no `--host`.

**Windows:** Propriedades do adaptador com internet → aba Compartilhamento → "Permitir que outros usuários da rede se conectem através da conexão à Internet deste computador" → selecionar o adaptador Ethernet do cabo. O Windows atribui `192.168.137.x` pra outra ponta.

### Opção 3 — IP automático link-local (APIPA / Zeroconf), sem configurar nada

Se nenhuma das duas pontas tiver IP configurado nem DHCP, Linux e Windows caem sozinhos, depois de alguns segundos, numa faixa `169.254.x.x/16` (protocolo IPv4LL / Zeroconf, via `avahi-autoipd` no Linux ou APIPA no Windows) — desde que essa fila não esteja desabilitada.

Não precisa mexer em nada: só esperar (pode levar 30–60s) e depois checar o IP atribuído com `ip a` (Linux) ou `ipconfig` (Windows). Usar esse IP `169.254.x.x` no `--host`.

**Menos confiável pra correção ao vivo** — depende de cada SO ter esse fallback ativado e do tempo de espera. Usar como plano B, não como plano principal.

---

## Conexão via Wi-Fi

### Opção 1 — Mesma rede Wi-Fi (roteador comum)

Se as duas máquinas conectarem no mesmo roteador/AP, já recebem IP via DHCP automaticamente — sem config extra.
```
ip a          # Linux: ver IP da interface wifi (wlan0/wlp...)
hostname -I   # alternativa rápida
ipconfig      # Windows
```
Usar o IP encontrado no `--host` do sender.

### Opção 2 — Hotspot local (sem roteador comum disponível)

Uma máquina cria um hotspot Wi-Fi, a outra conecta nele.

**Linux (NetworkManager):**
```
nmcli device wifi hotspot ifname wlan0 ssid teste-rede password "12345678"
```
Depois conectar a outra máquina nessa rede normalmente pela interface gráfica. A máquina que criou o hotspot fica geralmente em `10.42.0.1`.

**Windows:** Configurações → Rede e Internet → Hotspot Móvel → ativar, definir SSID/senha.

### Opção 3 — Wi-Fi Direct

Conexão par-a-par entre placas Wi-Fi sem precisar de roteador nem hotspot dedicado. Suporte varia por driver/SO (no Linux geralmente via `wpa_cli p2p_*` ou `iw dev`; no Windows via "Wi-Fi Direct" no gerenciador de dispositivos). Mais complexo de configurar na hora — citado aqui como opção existente, mas não recomendado pra correção ao vivo por causa da variabilidade de suporte.

---

## Firewall

Independente do método de conexão, se a porta `5555` (ou a que for passada em `--port`) estiver bloqueada no firewall da máquina do receiver, o sender não vai conseguir chegar nos pacotes.

**Linux (ufw):**
```
sudo ufw allow 5555/udp
sudo ufw allow 5555/tcp
```

**Linux (firewalld):**
```
sudo firewall-cmd --add-port=5555/udp --permanent
sudo firewall-cmd --add-port=5555/tcp --permanent
sudo firewall-cmd --reload
```

**Windows:** Firewall do Windows Defender → Configurações Avançadas → Regra de Entrada → Nova Regra → Porta → TCP/UDP `5555` → Permitir.

---

## Resumo — qual opção usar na correção

| Cenário | Recomendação |
|---|---|
| Cabo, rápido e confiável | IP estático (Opção 1) |
| Cabo, sem tempo pra configurar IP em cada ponta | Compartilhamento de conexão (Opção 2) |
| Cabo, plano B sem nenhuma config | Link-local automático (Opção 3), aceitando esperar |
| Wi-Fi, mesma rede do laboratório | Mesma rede (Opção 1) |
| Wi-Fi, sem rede comum disponível | Hotspot local (Opção 2) |
