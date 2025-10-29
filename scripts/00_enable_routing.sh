#!/bin/bash
# Habilita o encaminhamento de pacotes no kernel (transforma o Linux em um roteador)

echo "Habilitando encaminhamento de IP..."

# A 'flag' 1 ativa o encaminhamento
echo 1 > /proc/sys/net/ipv4/ip_forward

# Esta regra de 'nat' é crucial. Ela "traduz" os IPs privados da sua
# rede interna (ex: 192.168.1.10) para o IP público do seu roteador,
# permitindo que eles acessem a internet.
# (Ajuste 'eth0' para ser sua interface de SAÍDA/Internet)

echo "Configurando NAT (Masquerade) na interface de saída..."
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

echo "Roteamento habilitado."