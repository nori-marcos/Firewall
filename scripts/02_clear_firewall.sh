#!/bin/bash
# Limpa TODAS as regras de filtro e reseta as políticas

echo "Limpando regras do firewall e reabrindo tudo..."

# Limpa todas as regras
iptables -F       # Limpa a chain FORWARD, INPUT, OUTPUT
iptables -X       # Apaga chains personalizadas

# Limpa a tabela NAT (importante para remover a regra do enable_routing.sh)
iptables -t nat -F
iptables -t nat -X

# Reseta as políticas padrão para ACCEPT (permite tudo)
# Isso abre seu firewall completamente.
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

echo "Firewall limpo. Todo o tráfego está permitido."