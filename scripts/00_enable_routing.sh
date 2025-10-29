#!/bin/bash
# Habilita roteamento e NAT de forma persistente.

# Interface de saída para a internet, conectada ao provedor
WAN_IF="${WAN_IF:-eth0}"
# Interface de rede interna, utilizada pelos clientes para se conectar ao roteador
LAN_IF="${LAN_IF:-eth1}"
# Endereço IP da rede interna (LAN)
LAN_IP="${LAN_IP:-192.168.50.1/24}"

echo "[+] Ativando roteamento IPv4..."
sysctl -w net.ipv4.ip_forward=1
sed -i 's/^#\?net.ipv4.ip_forward.*/net.ipv4.ip_forward=1/' /etc/sysctl.conf

echo "[+] Configurando IP da LAN..."
ip addr add $LAN_IP dev $LAN_IF
ip link set $LAN_IF up

echo "[+] Limpando regras antigas..."
iptables -t nat -F

echo "[+] Ativando NAT (masquerade) na interface $WAN_IF..."
iptables -t nat -A POSTROUTING -o $WAN_IF -j MASQUERADE

echo "[✓] Roteamento e NAT configurados."
