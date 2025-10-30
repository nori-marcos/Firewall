#!/bin/bash

# --- 0. Definições ---
REDE_INTERNA="192.168.50.0/24"
SERVIDOR_INTERNO="192.168.50.20"

echo "[+] Limpando regras... (Apenas da tabela FILTER)"
iptables -F
iptables -X

echo "[+] Políticas padrão: Seguras (Bloqueia tudo por padrão)"
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

echo "[+] INPUT: Permitir tráfego de loopback"
iptables -A INPUT -i lo -j ACCEPT

echo "[+] INPUT: Permitir conexões estabelecidas"
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

echo "[+] INPUT: Permitir acesso ao servidor web (porta 8000)"
iptables -A INPUT -s $REDE_INTERNA -p tcp --dport 8000 -m state --state NEW -j ACCEPT

echo "[+] INPUT: Permitir Ping (ICMP) da rede interna"
iptables -A INPUT -s $REDE_INTERNA -p icmp --icmp-type echo-request -j ACCEPT

echo "[+] FORWARD: Permitir conexões estabelecidas"
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

echo "[+] FORWARD: Bloqueando DNS para redes sociais (String Match)"
iptables -A FORWARD -s $REDE_INTERNA -p udp --dport 53 -m string --string "facebook" --algo bm -j REJECT
iptables -A FORWARD -s $REDE_INTERNA -p udp --dport 53 -m string --string "tiktok" --algo bm -j REJECT

echo "[+] FORWARD: Permitir DNS (UDP e TCP) de saída (Geral)"
iptables -A FORWARD -s $REDE_INTERNA -p udp --dport 53 -m state --state NEW -j ACCEPT
iptables -A FORWARD -s $REDE_INTERNA -p tcp --dport 53 -m state --state NEW -j ACCEPT

echo "[+] FORWARD: Permitir HTTP e HTTPS de saída"
iptables -A FORWARD -s $REDE_INTERNA -p tcp --dport 80 -m state --state NEW -j ACCEPT
iptables -A FORWARD -s $REDE_INTERNA -p tcp --dport 443 -m state --state NEW -j ACCEPT

echo "[+] FORWARD: ICMP (Ping) gerenciado"
iptables -A FORWARD -s $REDE_INTERNA -d $SERVIDOR_INTERNO -p icmp --icmp-type echo-request -j ACCEPT
iptables -A FORWARD -s $REDE_INTERNA -p icmp --icmp-type echo-request -j REJECT --reject-with icmp-host-prohibited

echo "[✓] Regras de firewall aplicadas."