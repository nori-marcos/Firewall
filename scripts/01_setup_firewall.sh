#!/bin/bash
# Aplica as regras de firewall específicas do Trabalho 3

echo "Aplicando regras de firewall..."

# --- 0. Definições ---
REDE_INTERNA="192.168.1.0/24"
SERVIDOR_INTERNO="192.168.1.100"
IP_SOCIAL_1="157.240.22.35"
IP_SOCIAL_2="31.13.71.36"

# --- 1. Política Padrão ---
# Primeiro, bloqueia todo o tráfego que passa pelo roteador
iptables -P FORWARD DROP

# --- 2. Regras de Permissão ---
# Regra 1: Permite conexões estabelecidas (tráfego de resposta) [cite: 22]
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# Regra 1: Permite novas conexões HTTP/S de saída [cite: 22]
iptables -A FORWARD -s $REDE_INTERNA -p tcp --dport 80 -m state --state NEW -j ACCEPT
iptables -A FORWARD -s $REDE_INTERNA -p tcp --dport 443 -m state --state NEW -j ACCEPT

# Regra 2: Permite ICMP (ping) para o SERVIDOR INTERNO [cite: 25]
iptables -A FORWARD -s $REDE_INTERNA -d $SERVIDOR_INTERNO -p icmp --icmp-type echo-request -j ACCEPT

# --- 3. Regras de Bloqueio (O que sobrou será bloqueado pela política DROP) ---
# Regra 3: Bloqueia Redes Sociais [cite: 26]
# (Podemos tornar o bloqueio explícito para fins de log, se quisermos)
iptables -A FORWARD -s $REDE_INTERNA -d $IP_SOCIAL_1 -j DROP
iptables -A FORWARD -s $REDE_INTERNA -d $IP_SOCIAL_2 -j DROP

# Regra 2: Bloqueio de ICMP Externo [cite: 24]
# (Isso já é coberto pela política 'DROP', mas uma regra explícita é clara)
iptables -A FORWARD -s $REDE_INTERNA -p icmp --icmp-type echo-request -j DROP

echo "Regras de firewall aplicadas."