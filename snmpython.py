#!/usr/bin/env python
#-*-coding: utf-8-*-
# Autor: Isac Cavalcante
import pygame
from socket import *
from subprocess import Popen, PIPE
import os, time, sys
import bz2

global lista
lista = []
global lista_aux
lista_aux = []

log = ""

os.system("clear")

def banner():
    print ("-"*20).center(57, ' ')
    print "*** SNMPython v1.0 ***".center(57, ' ')
    print ("-"*20).center(57, ' ')

sb = socket(AF_INET, SOCK_DGRAM)
sb.bind(('', 9090))

def listar_agentes():
    cont = 1
    while True:
        try:
            os.system("clear")
            banner()
            print
            print "Mostrando agentes online. Aperte Ctrl+C para prosseguir."
            print
            for x in lista_aux:
                print x.split('\n')[0]
            time.sleep(3)
        except KeyboardInterrupt:
            os.system("clear")
            banner()
            print
            print "Agentes online:"
            print 
            for x in lista_aux:
                print x.split("\n")[0]
            print
            agente = raw_input("Escolha uma opção: ")
            ind = 0
            for x in lista_aux:
                if agente == x.split(")")[0]:
                    return lista[ind]
                else:
                    pass
                ind += 1
            
        
        dados, end = sb.recvfrom(1024)
        if end[0] not in lista:
            lista.append(end[0])
            lista_aux.append(str(cont)+') '+end[0] + " # " + dados)
            cont += 1
        else:
            pass


def enviar_email(TEXT, para):
    import smtplib
    SERVER = "smtp.gmail.com:587"
    FROM = "isac.servicosderedes@gmail.com"
    TO = [] # precisa ser uma lista
    TO.append(para)
    SUBJECT = "Relatório de Monitorização"
    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Enviando o email
    server = smtplib.SMTP(SERVER)
    server.ehlo()
    server.starttls()
    server.login("EMAIL", "SENHA")
    server.ehlo()
    server.sendmail(FROM, TO, message)
    server.quit()


def executar(comando):
    proc = Popen([comando], stdout=PIPE, shell=True)
    saida, erro = proc.communicate()
    return saida


def media_pings(para, n_pacotes):
    h = executar('date +\[%d\/%m\/%Y\ "-"\ %H:%M:%S\]\ ')
    h = h.split('\n')[0]
    cmd = "ping %s -c %s" % (para, n_pacotes)
    processo = Popen([cmd], stdout=PIPE, shell=True)
    print "Processando..."
    saida, erro = processo.communicate()
    if "/" not in saida:
        print
        print "%sO host está inalcançável." % h
        global log
        log += "%sO host está inalcançável." % h
    else:
        dados = saida.split("/")
        media = dados[4]
        rec = int(saida.split(',')[1].split()[0])
        per = n_pacotes - rec
        print
        print "%sA média entre tempo de resposta de %s pacotes do gerente para endereço %s é de %s milisegundos. Número de pacotes perdidos: %s\n" % (h, n_pacotes, para, media, per)
        global log
        log += "%sA média entre tempo de resposta de %s pacotes do gerente para endereço %s é de %s milisegundos. Número de pacotes perdidos: %s\n" % (h, n_pacotes, para, media, per)

def l():
    print '-'*118

banner()

#ip = raw_input("Digite o ip do host a ser monitorizado: ") 
ip = listar_agentes()

s = socket(AF_INET, SOCK_STREAM)

try:
    s.connect((ip, 3110))
except Exception, e:
    if e[0] == 111:
        print
        print "Conexão recusada. O agente está executando? "
        exit()
msg = s.recv(1024)


data =  msg.split("||")[0].split("\n")[0]
info =  msg.split("||")[1].split()

host = info[1]
ker = info[0]
ver = info[2]
arq = info[11] 

log += """
Relatório para o host: "%s"
Horário no host: %s
Kernel %s versão %s
Arquitetura: %s \n""" % (host, data, ker, ver, arq)

print """
Monitorizando host: "%s"
Horário no host: %s
Kernel %s versão %s
Arquitetura: %s """ % (host, data, ker, ver, arq)

def inicio():
    l()
    print """
1. Checar tempo de ping             6. Enviar relatório por email
2. Checar serviços habilitados      7. Sair
3. Checar interfaces de rede        
4. Visualizar relatório
5. Salvar relatório em arquivo
"""

    opcao = input("Escolha uma opção: ")
    
    if opcao == 1:
        def pin():
            print """
Checar tempo de ping
1. Do gerente para o agente
2. Do agente para um host
3. Voltar
"""
            op = input("Escolha uma opção: ")
            if op == 1:
                n = input("Digite o número de pacotes ICMP que serão enviados: ")
                media_pings(ip, n)
                l()
                pin()
            elif op == 2:
                end = raw_input("Digite o endereço IP do host a ser pingado: ")
                n = input("Digite o número de pacotes ICMP que serão enviados: ")
                print "Processando..."
                msg = "ping|||%s|||%s" % (end, n)
                s.send(msg)
                resposta = s.recv(1024)
                print
                print resposta
                global log
                log += resposta
                l()
                pin()
                
            elif op == 3:
                inicio()
            else:
                print "Opcão inválida."
                pin() # LOOP
        pin()

    elif opcao == 2:
        def serv():
            print """
Checar serviços habilitados
1. Apache
2. PostgresSQL
3. DNS
4. Voltar
"""
            op = input("Escolha uma opção: ")
            if op == 1:
                s.send("apache")
                resposta = s.recv(1024) 
                print
		print resposta
                l()
                global log
                log += resposta+'\n'
                serv()
               
            elif op == 2:
                s.send("postgres")
                resposta = s.recv(1024)
                print
                print resposta
                l()
                global log
                log += resposta+'\n'
                serv()

            elif op == 3:
                s.send("bind")
                resposta = s.recv(1024)
                print
                print resposta
                l()
                global log
                log += resposta+'\n'
                serv()

            elif op == 4:
                inicio()

            else:
                print "Opção inválida."
                serv()
        serv()

    elif opcao == 3:
        l()
        s.send("interfaces")
        time.sleep(5)
        resposta = s.recv(4096)
        print resposta
        global log
        log += "\n" + resposta + "\n"
        inicio()

    elif opcao == 4:
        l()
        print log
        inicio()

    elif opcao == 5:
        n = raw_input("Digite o nome do arquivo: ")
        arq = open(n, 'a')
        arq.write(log)
        arq.close()
        print "Relatório salvo em %s." % n
        inicio()

    elif opcao == 6:
	global log
        dest = raw_input("Digite o endereço de email: ")
        print "Enviando..."
        try:
            enviar_email(log, dest)
            print "Relatório enviado."
        except Exception, msg:
            print msg
        inicio()

    elif opcao == 7:
        print "Encerrando..."
        l()
        exit()

    else:
        print "Opção inválida."
        inicio()

inicio()
