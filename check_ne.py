import re
import telnetlib
import time
import os
import datetime
import threading

dslams_list = open("ne.txt", "r")
dslams_list.seek(0)
dslams = dslams_list.readlines()


os.system("mkdir $(date +%F)")

#Open telnet connection to devices
def open_telnet_conn(ip, dslam_name):
    #Change exception message
    try:
        #Define telnet parameters
        username = 'username'
        password = 'password'
     
        connection_timeout = 5
        reading_timeout = 5
        port =23

        connection = telnetlib.Telnet(ip, port, connection_timeout)
        
        router_output = connection.read_until("Username:", reading_timeout)
        connection.write(username + "\n")
        
        router_output = connection.read_until("Password:", reading_timeout)
        connection.write(password + "\n")
        time.sleep(1)	
 	
	#####################
	#####################
	connection.write("\n")      
        connection.write("###commands###\n")
        time.sleep(2)
 	#####################
	#####################
        
        router_output = connection.read_very_eager()

        #print router_output
	today = datetime.date.today()
	complete_path = os.path.join(str(today), dslam_name)
        f = open(complete_path, "w+")
	f.write(router_output)
	f.close()
        #Closing the connection
        connection.close()
        
    except IOError:
        print "Input parameter error! Please check username, password and file name."

def threading_rulz():
	threads = []
	for dslam in dslams:
		dslam_name,ip=dslam.split()
		print ip
		print dslam_name
		th = threading.Thread(target = open_telnet_conn, args = (ip, dslam_name))
		th.start()
		threads.append(th)
	for th in threads:
		th.join()
	#open_telnet_conn(ip, dslam_name)
threading_rulz()
