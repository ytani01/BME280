#!/usr/bin/env python3
#
import sys
import time
import json
import paho.mqtt.client as mqtt
from BME280I2C import BME280I2C

#####
MYNAME		= sys.argv[0]
HOSTNAME 	= 'mqtt.beebotte.com'
PORT		= 8883
CACERT		= 'mqtt.beebotte.com.pem'
BME280_ADDR	= 0x76

INTERVAL_SEC	= 300  # sec

#####
def print_usage():
    print()
    print('usage: {0} token_str channel resource'.format(MYNAME))
    print()

#####
def mqtt_publish(client, topic, data_json):
    client.connect(HOSTNAME, port=PORT, keepalive=60)
    client.publish(topic, data_json)
    time.sleep(1)
    client.disconnect()

#####
def main():
    if len(sys.argv) != 4:
        print_usage()
        sys.exit(1)

    token_str = sys.argv[1]
    ch_name = sys.argv[2]
    res_name = sys.argv[3]

    topic = ch_name + '/' + res_name
    print('topic: ' + topic)

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set('token:%s' % token_str)
    client.tls_set(CACERT)

    #data_val = {'data': {'temp': 0, 'humidity': 0, 'pressure': 0}, 'ispublic': True, 'ts': 0}
    data_val = {'data': {'temp': 0, 'humidity': 0, 'pressure': 0}, 'ts': 0}

    bme280 = BME280I2C(BME280_ADDR)

    while True:
        if not bme280.meas():
            print('Error: BME280')
            sys.exit(1)

        data_val['data']['temp']	= int(bme280.T * 100) / 100
        data_val['data']['humidity']	= int(bme280.H * 100) / 100
        data_val['data']['pressure']	= int(bme280.P)
        data_val['ts'] = int(time.time() * 1000)
        #print(data_val)

        data_json = json.dumps(data_val)
        print(data_json)

        mqtt_publish(client, topic, data_json)
            
        time.sleep(INTERVAL_SEC)
        
if __name__ == '__main__':
    main()
