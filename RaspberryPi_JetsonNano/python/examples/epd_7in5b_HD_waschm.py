#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'font')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_HD
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import urllib, json
import math

logging.basicConfig(level=logging.DEBUG)

def formatTemperature(temp):
    split_temp = str(temp).split(".") #split float into integer and fraction part
    temp_int = int(split_temp[0].zfill(2)) #zero padding
    if(split_temp[1] <=2 ): temp_frac=0 #round fraction part to 5 or 0
    elif(split_temp[1] >2 and  split_temp[1]<=7): temp_frac=5
    else :
        temp_frac=0
        temp_int += 1    
    return temp_int, temp_frac


try:
    temperature_url = 'https://www.kaiserslautern.de/export/baeder/waschmuehle_temperature.json'
    response = urllib.urlopen(temperature_url)
    data = json.loads(response.read())
    temperature_water = float(data['data']['external_temperature_1'])
    temperature_water_int, temperature_water_frac = formatTemperature(temperature_water)

    temperature_air = float(data['data']['temperature'])
    temperature_air_int, temperature_air_frac = formatTemperature(temperature_air)
    

    logging.debug(data)
    logging.debug("Wassertemperatur: " + str(temperature_water_int) + "." + str(temperature_water_frac))
    logging.debug("Lufttemperatur: " + str(temperature_air_int) + "." + str(temperature_air_frac))

    guest_counter_url = 'https://www3.kaiserslautern.de/smartcounter/json/counter.json'
    response = urllib.urlopen(guest_counter_url)
    data = json.loads(response.read())
    guest_counter = data[1]['counter']
    logging.info(data)
    logging.info("Aktuelle Besucherzahl: " + str(guest_counter))

except IOError as e:
    logging.info(e)

try:
    logging.info("epd7in5b_HD Demo")

    epd = epd7in5b_HD.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    padding = 40
    vmiddle = 264
    fontsize = 220
    fontsize0em66 = int(fontsize*0.66)
    fontsize0em33 = int(fontsize*0.33)

    font36 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), 36)
    font0em33 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), fontsize0em33)
    font0em66 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II.ttf'), fontsize0em66)
    font1em = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), fontsize)

    # Drawing on the Vertical image (resolution: 880x528)
    logging.info("1.Drawing on the Horizontal image...")
    black = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    red = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_black = ImageDraw.Draw(black)
    draw_red = ImageDraw.Draw(red)
    draw_black.text((padding, padding), str(temperature_air_int), font = font1em, fill = 0)
    draw_black.text((240, padding), "." + str(temperature_air_frac) + u"°C", font = font0em66, fill = 0)
    draw_black.text((240, padding+fontsize0em66-20), "Luft", font = font0em33, fill = 0)
    draw_black.line((10, vmiddle, 870, vmiddle), fill = 0)
    draw_black.text((padding, vmiddle+padding), str(temperature_water_int), font = font1em, fill = 0)
    draw_black.text((240, vmiddle+padding), "." + str(temperature_water_frac) + u"°C", font = font0em66, fill = 0)
    draw_black.text((240, vmiddle+padding+fontsize0em66-20), "Wasser", font = font0em33, fill = 0)
    draw_black.line((587, 10, 587, 518), fill = 0)

    #draw_black.text((100, 40), 'Aktuelle Besucher: '+ str(guest_counter), font = font24, fill = 0)
    epd.display(epd.getbuffer(black), epd.getbuffer(red))
    #time.sleep(5)

    #logging.info("Clear...")
    #epd.init()
    #epd.Clear()

    #logging.info("Goto Sleep...")
    #epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_HD.epdconfig.module_exit()
    exit()
