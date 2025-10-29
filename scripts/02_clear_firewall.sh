#!/bin/bash
# Limpa as regras da tabela FILTER e reseta a política FORWARD.
# Propositalmente NÃO mexe na tabela 'nat'.

echo "Limpando regras da tabela 'filter'..."

# Limpa todas as regras da tabela 'filter'
iptables -t filter -F FORWARD
iptables -t filter -F INPUT
iptables -t filter -F OUTPUT
iptables -t filter -X

# Reseta as políticas padrão para ACCEPT (permite tudo)
# Especialmente importante para a chain FORWARD, que estava como DROP
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

echo "[✓] Firewall (filter) limpo. Todo o tráfego está sendo encaminhado."