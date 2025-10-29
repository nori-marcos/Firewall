#!/bin/bash

# --- 0. Definições ---
REDE_INTERNA="192.168.50.0/24"
SERVIDOR_INTERNO="192.168.50.20"
SOCIAL_SET="socialblock"

echo "[+] Limpando regras..."
iptables -F
iptables -t nat -F
iptables -X

echo "[+] Políticas padrão: Seguras (Bloqueia tudo por padrão)"
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

echo "[+] Permitir tráfego de loopback (interno do roteador)"
iptables -A INPUT -i lo -j ACCEPT

echo "[+] Permitir conexões estabelecidas (essencial para o firewall funcionar)"
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

echo "[+] 1) HTTP e HTTPS de saída permitidos"
iptables -A FORWARD -s $REDE_INTERNA -p tcp --dport 80 -m state --state NEW -j ACCEPT
iptables -A FORWARD -s $REDE_INTERNA -p tcp --dport 443 -m state --state NEW -j ACCEPT

echo "[+] 2) ICMP (Ping) gerenciado"
iptables -A FORWARD -s $REDE_INTERNA -d $SERVIDOR_INTERNO -p icmp --icmp-type echo-request -j ACCEPT

iptables -A FORWARD -s $REDE_INTERNA -p icmp --icmp-type echo-request -j REJECT --reject-with icmp-host-prohibited

echo "[+] 3) Bloqueio de redes sociais (via ipset)"
ipset list $SOCIAL_SET >/dev/null 2>&1 || ipset create $SOCIAL_SET hash:ip

# ipset add $SOCIAL_SET 157.240.22.35
# ipset add $SOCIAL_SET 157.240.23.35

iptables -A FORWARD -s $REDE_INTERNA -m set --match-set $SOCIAL_SET dst -j REJECT

echo "[✓] Regras de firewall aplicadas."