#!/usr/bin/env python3
#
import sys
import time
from BME280I2C import BME280I2C
import click
from beebotte import *

#####
MYNAME		= sys.argv[0]
HOSTNAME 	= 'api.beebotte.com'
#PORT		= 8883
#CACERT		= '/home/pi/mqtt.beebotte.com.pem'
BME280_ADDR	= 0x76

DEF_OUTFILE	= 'out.csv'
DEF_INTERVAL	= 300  # sec

#####
@click.command(help='BME280 MQTT publisher (temp, humidiy, pressure)')
@click.argument('token_str', default='')
@click.argument('ch_name', default='')
@click.option('--interval', '-i', type=int, default=0,
              help='interval seconds')
@click.option('--outfile', '-o', type=click.Path(), default='',
              help='output file name')
def main(token_str, ch_name, interval, outfile):
    if interval == 0:
        interval = DEF_INTERVAL
    if outfile == '':
        outfile = DEF_OUTFILE
    print('token_str: %s' % token_str)
    print('ch_name: %s' % ch_name)
    print('interval: %d' % interval)
    print('outfile: %s' % outfile)

    bbt = BBT(token=token_str, hostname=HOSTNAME)
    bme280 = BME280I2C(BME280_ADDR)

    prev_temp = 0.0
    prev_humidity = 0.0
    prev_pressure = 0
    prev_sec = 0
    while True:
        if not bme280.meas():
            print('Error: BME280')
            sys.exit(1)

        ts_now = time.time()
        ts_str = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(ts_now))

        update_flag = {
            'temp':	False,
            'humidity':	False,
            'pressure':	False,
            'time':	False	}
        
        if abs(bme280.T - prev_temp) >= 0.5:
            print("T")
            update_flag['t'] = True
            prev_temp = bme280.T
        
            bbt.write(ch_name, "temp", bme280.T)

        if abs(bme280.H - prev_humidity) >= 5:
            print("H")
            update_flag['h'] = True
            prev_humidity = bme280.H

            bbt.write(ch_name, "humidity", bme280.H)

        if abs(bme280.P - prev_pressure) >= 2:
            update_flag['p'] = True
            prev_pressure = bme280.P

            bbt.write(ch_name, "pressure", round(bme280.P))

        if ts_now - prev_sec > interval:
            update_flag['time'] = True

            bbt.write(ch_name, "temp", bme280.T)
            bbt.write(ch_name, "humidity", bme280.H)
            bbt.write(ch_name, "pressure", bme280.P)
            
        out_str = '%d ' % ts_now
        if update_flag['time']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%s ' % ts_str
        if update_flag['t']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%.1f C ' % bme280.T
        if update_flag['h']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%.1f %% ' % bme280.H
        if update_flag['p']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%d hPa ' % bme280.P
        print(out_str)

        if True in update_flag.values():
            prev_sec = ts_now

            with open(outfile, mode='a') as f:
                f.write(out_str + '\n')

        time.sleep(5)
            
if __name__ == '__main__':
    main()
