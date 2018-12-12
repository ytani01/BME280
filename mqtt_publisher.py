#!/usr/bin/env python3

import sys
import time
import json
import paho.mqtt.client as mqtt

print(len(sys.argv))
if len(sys.argv) != 5:
    print('usage: ' + sys.argv[0] + ' token_str channel resouce value')
    sys.exit(1)

token_str = sys.argv[1]
channel_name = sys.argv[2]
resource_name = sys.argv[3]
data_value = sys.argv[4]

HOSTNAME = "mqtt.beebotte.com"
TOKEN = sys.argv[1]
PORT = 8883
TOPIC = channel_name + '/' + resource_name
CACERT = "mqtt.beebotte.com.pem"

print('TOKEN=' + TOKEN)
print('TOPIC=' + TOPIC)

client = mqtt.Client(protocol=mqtt.MQTTv311)

client.username_pw_set('token:%s' % TOKEN)
client.tls_set(CACERT)

client.connect(HOSTNAME, port=PORT, keepalive=60)
data_dic = {}
data_dic['data'] = float(data_value)
data_dic['ispublic'] = True
data_dic['ts'] = int(time.time() * 1000)
#data_dic['ispublic'] = True
data_json = json.dumps(data_dic)
print(data_json)
time.sleep(1)
client.publish(TOPIC, data_json)
client.disconnect()
