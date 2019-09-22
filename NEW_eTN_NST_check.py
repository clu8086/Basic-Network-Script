import re
import time
import os
import datetime
import threading
import paramiko
import base64
import csv

os.system("cp /dev/null  logs.txt")
ne_list = open("ISIS_Noduri_28-08-2019.txt", "r")
ne_list.seek(0)
nes = ne_list.readlines()

with open(("eTN_NST_CHECK_"+str("{:%d-%m-%Y}".format(datetime.date.today()))+".csv"), 'a') as csv_file:
        c = csv.writer(csv_file)
        c.writerow(['NE','MPLS NST Res'])

def connect(ip, ne):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username = base64.b64decode("xxxxxxxxxxxxxxxxx"), password = base64.b64decode("xxxxxxxxxxxxxxxxxxx="))
        conn = ssh.invoke_shell()
        return conn, ssh

def send_cmd(ssh_connection, cmd_list):
        for cmd in cmd_list:
                ssh_connection.send(cmd+'\n')
                time.sleep(5)

def out(ssh_connection, buffer=65535):
        output = ssh_connection.recv(buffer)
        return output

def parse_output(output):
        CheckResm = bool("V200R003" in output)
        return CheckResm

def parse_resm(output, ne):
        for line in output.split():
                if 'RestNum' in line:
                        val = line.strip().split('=')[1].split(',')[0]
                        print ne, val
                        with open(("eTN_NST_CHECK_"+str("{:%d-%m-%Y}".format(datetime.date.today()))+".csv"), 'a') as csv_file:
                                c = csv.writer(csv_file)
                                c.writerow([ne, val])


disp_version = ["screen-length 0 temporary\n", "\n", "dis version\n"]
disp_resm_poolinfo = ["system-view\n", "\n", "diagnose\n", "display resm poolinfo 7\n"]

def main(ip, ne):
        try:
                ssh_connection, ssh_client = connect(ip, ne)
                send_cmd(ssh_connection, disp_version)
                output = out(ssh_connection)
                if parse_output(output):
                        send_cmd(ssh_connection, disp_resm_poolinfo)
                        output = out(ssh_connection)
                        parse_resm(output, ne)
                        ssh_client.close()
                else:
                        ssh_client.close()
        except Exception as e:
                print e
                print "Connection failed for "  +ne+"; "+" Cause: "+str(e)
                log = open("logs.txt", "a+")
                print >>log, "Connection failed for " +ne+"; "+" Cause: "+str(e)
                log.close()

if __name__ == "__main__":
        threads = []
        for line in nes:
                ip, ne = line.split()
                print ip, ne

                th = threading.Thread(target = main, args = (ip, ne))
                th.start()
                threads.append(th)
        for th in threads:
                th.join()
