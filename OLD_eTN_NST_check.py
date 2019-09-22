import re
import time
import os
import datetime
import threading
import paramiko
import base64
import subprocess

#os.system("mkdir $(date +%d-%m-%Y)")
ne_list = open("ne_list_11_03_2019.txt", "r")
ne_list.seek(0)
nes = ne_list.readlines()
rpath = os.path.join(str("{:%d-%m-%Y}".format(datetime.date.today())), "results.txt")
lpath = os.path.join(str("{:%d-%m-%Y}".format(datetime.date.today())), "logs.txt")

def ssh_connection(ip, ne, atn_type):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username = base64.b64decode("xxxxxxxxxxxxxxxxxxxxx"), password = base64.b64decode("xxxxxxxxxxxxxxxxxxx="), timeout = 10)

        conn = ssh.invoke_shell()
        conn.send("\n")
        conn.send("screen-length 0 temporary\n")
        time.sleep(3)
        conn.send("display version\n")
        time.sleep(4)

        output = conn.recv(65535)
        path = os.path.join(str("{:%d-%m-%Y}".format(datetime.date.today())), ne)
        out = open(path, "w+")
        out.write(output)
        out.close()
        log = open(lpath, "a+")

        if re.search("V200R005C10SPC100", output, re.MULTILINE):
                print "NE " + ne +" "+atn_type+ "  is updated"
                print >>log, "NE " + ne +" "+atn_type+ "  is updated"
                ssh.close()
        else:
                print "NE " + ne + " is not updated, checking MPLS table resources..."
                print >>log, "NE " + ne + " is not updated, checking MPLS table resources..."
                conn.send("system-view\n")
                time.sleep(3)
                conn.send("diagnose\n")
                time.sleep(3)
                conn.send("display resm poolinfo 7\n")
                time.sleep(3)
                conn.send("return\n")
                time.sleep(3)
                output = conn.recv(65535)
                for item in output.split():
                        if re.search('RestNum+', item):
                                item = item
                                break
                val1 = item.split(',')[0]
                print val1
                print >>log, val1
                val = item.split(',')[0].split('=')[1]
                print "RestNum value for " +ne+" "+atn_type+ " is " +val
                print >>log, "RestNum value for " +ne+" "+atn_type+ " is " +val
                if int(val) <= 20000:
                        results = open(rpath, "a+")
                        results.write("NE " +ne+":::"+atn_type+"::: has low MPLS table resources " +val1+"\n")
                        results.close()

        path = os.path.join(str("{:%d-%m-%Y}".format(datetime.date.today())), ne)
        out = open(path, "a+")
        out.write(output)
        out.close()
        log.close()
        ssh.close()
    except Exception as e:
        print e
        print "Connection failed for "  +ne+";"
        #print >>log, "Connection failed for "  +ne
        #log.close()
def thr():
        threads = []
        for line in nes:
                ne, atn_type, ip =  line.split()
                #ssh_connection(ip, ne)
                th = threading.Thread(target = ssh_connection, args = (ip, ne, atn_type))
                print ip, ne
                th.start()
                time.sleep(0.5)
                #print threading.active_count()
                threads.append(th)
        for th in threads:
                th.join()
thr()

#os.system('cd $(date +%d-%m-%Y)')
#os.system('sort -n -t= -k2 $(date +%d-%m-%Y)/results.txt > $(date +%d-%m-%Y)/results_sorted.txt')
#os.system('mailx -s "eTN MPLS Resources Check" -r hal9000@discovery.com vasile.cretu@vodafone.com < $(date +%d-%m-%Y)/results_sorted.txt')
