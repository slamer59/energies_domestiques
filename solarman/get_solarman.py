#!/usr/bin/python
# -*- coding: utf8 -*-
# Lecture sur Solarman
# --------------------
# http://www.steves-internet-guide.com/simple-python-mqtt-topic-logger/
import requests
from datetime import datetime
import paho.mqtt.client as mqtt
import logging
import json
from decouple import config

import time
import random

BROKER_URL = config("BROKER_URL")
UPDATE_DATA_TIME = config("UPDATE_DATA_TIME", cast=int)
REMEMBER_ME_SOLARMAN = config("REMEMBER_ME_SOLARMAN")

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
port=1883

def on_publish(client,userdata,result):
    print("SolarmanPV : Data published.")
    pass


def has_changed(topic,msg):
    topic2=topic.lower()
    if topic2.find("control")!=-1:
        return False
    if topic in last_message:
        if last_message[topic]==msg:
            return False
    last_message[topic]=msg
    return True


def read_solarman():

    cookies = {
        'language': '7', 
        'autoLogin': 'on', 
        'Language': 'fr', 
        'rememberMe': REMEMBER_ME_SOLARMAN, 
        'timeOffset': 'undefined', 
        'JSESSIONID': '90093f39-1e19-4db7-a9c8-12ea15a4a561',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://home.solarman.cn/device/inverter/view.html?v=2.3.0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    data = {
        'deviceId': '102302994'
    }

    data = requests.post('https://home.solarman.cn/cpro/device/inverter/goDetailAjax.json', headers=headers, cookies=cookies, data=data).json()['result']['deviceWapper']  

    MQTT_TOPIC_2 = "SolarmanPV_TP"
    lst = ['realTimeDataBattery','realTimeDataElect','realTimeDataImp','realTimeDataPower','realTimeDataTemp']
    for champs in lst:
        MQTT_MSG ={info['name']:info["value"] for info in data[champs]}
        now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        MQTT_MSG['time'] = now
        
        for k, v in MQTT_MSG.items():
            try:
                MQTT_MSG[k] = float(v)
            except:
                MQTT_MSG[k] = v
                pass
        # if has_changed(client,topic,msg):
        msg_info = client.publish(MQTT_TOPIC_2 + "/" + champs, json.dumps(MQTT_MSG), 1)
        if msg_info.is_published() == False:
            logging.warning("Message is not yet published.")

        # This call will block until the message is published.
        msg_info.wait_for_publish()
    logging.info("Write done")

def on_disconnect(client, userdata,rc=0):
    logging.debug("DisConnected result code "+str(rc))
    client.loop_stop()

while 1:
    client = mqtt.Client()
    client.loop_start()
    
    client.enable_logger(logger)
    
    client.on_publish = on_publish
    client.connect(BROKER_URL, port)
    read_solarman()
    client.disconnect()
    client.loop_stop()
    time.sleep(UPDATE_DATA_TIME)
