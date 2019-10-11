import sys
import os
import base64
import threading
import logging
import sqlite3
from lxml import etree
from ncclient import manager
from ncclient import operations

log = logging.getLogger(__name__)
ne_list = open("AG_ISIS_Noduri_25-09-2019.txt", "r")
ne_list.seek(0)
nes = ne_list.readlines()

FILTER = '''<devm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
                <cpuInfos/>
            </devm>'''

# Fill the device information and establish a NETCONF session
def huawei_connect(host, port, user, password):
    return manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           hostkey_verify = False,
                           device_params={'name': "huawei"},
                           allow_agent = False,
                           look_for_keys = False)

def parse_xml(ne, xml):
    ne_dict = {}
    ne_dict[ne] = {}
    #print ne
    root = etree.fromstring(xml)
    for data in root.getchildren():
        for devm in data.getchildren():
            for cpuinfos in devm.getchildren():
                for cpuinfo in cpuinfos.getchildren():
                    #print cpuinfo.tag, cpuinfo.text
                    if 'position' in cpuinfo.tag:
                        card = cpuinfo.text
                    elif 'systemCpuUsage' in cpuinfo.tag:
                        cpu = cpuinfo.text
                        #print card, cpu
                        ne_dict[ne][card] = cpu
    return ne_dict

def database_insert(ne, xml):
    db = sqlite3.connect('test.db')
    cursor = db.cursor()
    data = parse_xml(ne, xml)
    create="create table if not exists {}(Card Int, CPU Int, t REAL DEFAULT (datetime('now', 'localtime')));".format(ne)
    try:
        cursor.execute(create)
    except Exception as e:
        print(e)
    for k,v in data[ne].items():
        values = '{}, {}'.format(k, v)
        insert = "INSERT INTO {} VALUES({}, {});".format(ne, values, "datetime('now')")
        cursor.execute(insert)

    db.commit()
    db.close()

def test_get(host, ne, port=22, user=base64.b64decode("xxxxxxxxxxxxxxxx"), password=base64.b64decode("xxxxxxxxxxxxxxxx")):
    #1.Create a NETCONF session
    try:
        with huawei_connect(host, port=port, user=user, password=password) as m:
            n = m._session.id
            print("The session id is %s." % (n))
            #print ne
            #2.Send get RPC and print RPC reply
            get_reply = m.get(("subtree", FILTER))
            #print(get_reply)
            string_get_reply = etree.tostring(get_reply.data_ele, pretty_print=True)
            parse_xml(ne, string_get_reply)
            database_insert(ne, string_get_reply)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    threads=[]
    for line in nes:
        ip, ne = line.split()
        th = threading.Thread(target = test_get, args = (ip, ne))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
