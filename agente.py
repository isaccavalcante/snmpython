#!/usr/bin/env python
#-*-coding: utf-8-*-
# Autor: Isac Cavalcante
from socket import *
import time, os
from subprocess import Popen, PIPE
from threading import Thread

# LIBERANDO A PORTA
os.system("fuser -k 3110/tcp")
time.sleep(3)

# SOCKET BROADCAST
sb = socket(AF_INET, SOCK_DGRAM)
sb.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sb.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

# SOCKET TCP
s = socket(AF_INET, SOCK_STREAM)
s.bind(("", 3110))
s.listen(5)

# FUNÇÕES
def executar(comando):
    proc = Popen([comando], stdout=PIPE, shell=True)
    saida, erro = proc.communicate()
    return saida

def descoberta():
    host = executar("hostname")
    while True:
        sb.sendto(host,('<broadcast>', 9090))
        time.sleep(5)

def media_pings(para, n_pacotes):
    cmd = "ping %s -c %s" % (para, n_pacotes)
    processo = Popen([cmd], stdout=PIPE, shell=True)
    saida, erro = processo.communicate()
    if "/" not in saida:
        return "O host está inalcançável."
    else:
        dados = saida.split("/")
        media = dados[5]
        rec = int(saida.split(',')[1].split()[0])
        per = int(n_pacotes) - rec

        return "A média entre tempo de resposta de %s pacotes do agente para endereço %s é de %s milisegundos. Número de pacotes perdidos: %s" % (n_pacotes, para, media, per)

def executar(comando):
    proc = Popen([comando], stdout=PIPE, shell=True)
    saida, erro = proc.communicate()
    return saida

# INÍCIO
t = Thread(target=descoberta)
t.start()
print "Protocolo de descoberta \t\t [OK]"
c, e = s.accept()
print "Gerente conectado (%s) \t [OK]" % e[0]
saida1 = executar('date +%A,\ %d\ "de"\ %B\ "de"\ %Y\ "-"\ %H:%M:%S')
saida2 = executar('uname -a')
msg = "%s||%s" % (saida1, saida2)
c.send(msg)
    
# LOOP
while True:
    req = c.recv(1024)
    if "ping" in req:
	to = req.split('|||')[1]
        n = req.split('|||')[2]
        #------------------
        h = executar('date +\[%d\/%m\/%Y\ "-"\ %H:%M:%S\]\ ')
        h = h.split('\n')[0]
        r = media_pings(to, n)
        resposta = h+r
        c.send(resposta)
        #------------------
            
    elif "apache" in req:
        r = executar("service apache2 status")
        if "not running" in r:
            r = "Servidor Apache não está executando."
        elif "running" in r:
            r = "Servidor Apache está executando."
        elif "unrecognized" in r:
            r = "Servidor Apache não está instalado."
        #------------------
        h = executar('date +\[%d\/%m\/%Y\ "-"\ %H:%M:%S\]\ ')
        h = h.split('\n')[0]
        resposta = h+r
        c.send(resposta)
        #------------------
            
    elif "postgres" in req:
        r = executar("service postgresql status")
        if "online" in r:
            p = r.split()[2].replace("):", "")
            r = "Servidor de banco de dados PostgresSQL está executando na porta %s." % p
        elif "down" in r:
            r = "Servidor de banco de dados PostgresSQL não está executando."
        elif "unrecognized" in r:
            r = "Servidor de banco de dados PoStgresSQL não está instalado."
        #------------------
        h = executar('date +\[%d\/%m\/%Y\ "-"\ %H:%M:%S\]\ ')
        h = h.split('\n')[0]
        resposta = h+r
        c.send(resposta)
        #------------------

    elif "bind" in req:
        r = executar("service bind9 status")
        if "not running" in r:
            r = "Servidor DNS não está executando."
        elif "running" in r:
            r = "Servidor DNS está executando."
        elif "unrecognized" in r:
            r = "Servidor DNS não está instalado."
        #------------------
        h = executar('date +\[%d\/%m\/%Y\ "-"\ %H:%M:%S\]\ ')
        h = h.split('\n')[0]
        resposta = h+r
        c.send(resposta)
        #------------------

    elif "interface" in req:
        r = executar("ifconfig")
        h = executar('date +\[%d\/%m\/%Y\ "-"\ %H:%M:%S\]\ ')                            
        resposta = h.split('\n')[0] + "Interfaces de rede: \n" + r
        c.send(resposta)

    else:
        pass
