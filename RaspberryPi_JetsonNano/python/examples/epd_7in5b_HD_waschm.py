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
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)


padding = 40
vmiddle = 264
vline = 530
fontsize = 264
fontsize0em66 = int(fontsize*0.66)
fontsize0em33 = int(fontsize*0.33-10)

fontsize_clock = 100
fontsize_clock0em66 = int(fontsize_clock*0.66)
fontsize_clock0em50 = int(fontsize_clock*0.50)
fontsize_clock0em33 = int(fontsize_clock*0.33)

font0em33 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II.ttf'), fontsize0em33)
font0em66 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), fontsize0em66)
font1em = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), fontsize)

font_clock1em = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), fontsize_clock)
font_clock0em66 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), fontsize_clock0em66)
font_clock0em50 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), fontsize_clock0em50)
font_clock0em33 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II.ttf'), fontsize_clock0em33)


def formatTemperature(temp):
    split_temp = str(temp).split(".") #split float into integer and fraction part
    temp_int = int(split_temp[0].zfill(2)) #zero padding
    if(split_temp[1] <=2 ): 
        temp_frac=0 #round fraction part to 5 or 0
    elif(split_temp[1] >2 and  split_temp[1]<=7): 
        temp_frac=5
    else :
        temp_frac=0
        temp_int += 1    
    return temp_int, temp_frac


def getData(): #ToDo: Exeption handling, if ressource is unavailable or data is invalid
    logging.info("Retrieving Data...")
    #Sensordata
    temperature_url = 'https://www.kaiserslautern.de/export/baeder/waschmuehle_temperature.json'
    response = urllib.urlopen(temperature_url)
    data = json.loads(response.read())
    temperature_water = float(data['data']['external_temperature_1'])
    temperature_water_int, temperature_water_frac = formatTemperature(temperature_water)

    temperature_air = float(data['data']['temperature'])
    temperature_air_int, temperature_air_frac = formatTemperature(temperature_air)
    
    #date and time
    now = datetime.now()
    time_hours = now.strftime("%H")
    time_minutes = now.strftime("%M")
    time_year = now.strftime("%Y")
    time_date = now.strftime("%d.%m.")

    #weather 
    temperature_url = 'https://www.kaiserslautern.de/export/wetter/dwd_wetter_morlautern.json'
    response = urllib.urlopen(temperature_url)
    logging.debug(response)
    data = json.loads(response.read())
    precipitation = float(data['precipitation_perc'])

    result = {
        "temperature_water_int" : temperature_water_int,
        "temperature_water_frac" : temperature_water_frac,
        "temperature_air_int" : temperature_air_int,
        "temperature_air_frac" : temperature_air_frac,
        "time_hours" : time_hours,
        "time_minutes" : time_minutes,
        "time_year" : time_year,
        "time_date" : time_date,
        "precipitation" : precipitation
    }
    logging.debug("Recieved Data: " + str(result))
    return result

def initBuffer():
    # (resolution: 880x528)
    logging.info("Initialising Buffer...")
    black = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    red = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    return black, red
    


def fillBuffer(data, black, red):
    logging.info("Fill Image Buffer...")
    draw_black = ImageDraw.Draw(black)
    #draw_red = ImageDraw.Draw(red)
    #Temperatures
    draw_black.text((padding, padding), str(data["temperature_air_int"]), font = font1em, fill = 0)
    draw_black.text((290, padding), "." + str(data["temperature_air_frac"]) + u"°C", font = font0em66, fill = 0)
    draw_black.text((290, padding+fontsize0em66-30), "Luft", font = font0em33, fill = 0)
    draw_black.line((10, vmiddle, vline, vmiddle), fill = 0) # horizontal line
    draw_black.text((padding, vmiddle+padding), str(data["temperature_water_int"]), font = font1em, fill = 0)
    draw_black.text((290, vmiddle+padding), "." + str(data["temperature_water_frac"]) + u"°C", font = font0em66, fill = 0)
    draw_black.text((290, vmiddle+padding+fontsize0em66-30), "Wasser", font = font0em33, fill = 0)
    draw_black.line((vline, 10, vline, 518), fill = 0) #vertical Line

    #Time
    draw_black.text((vline+0.5*padding, padding), data["time_hours"], font = font_clock1em, fill = 0)
    draw_black.text((vline+0.5*padding+fontsize_clock, padding), data["time_minutes"], font = font_clock0em66, fill = 0)
    draw_black.text((vline+0.5*padding+fontsize_clock, padding+fontsize_clock0em66-5), "Uhr", font = font_clock0em33, fill = 0)

    #Date
    draw_black.text((vline+0.5*padding+fontsize_clock+fontsize_clock0em66+padding, padding), data["time_date"], font = font_clock0em50, fill = 0)
    draw_black.text((vline+0.5*padding+fontsize_clock+fontsize_clock0em66+padding, padding+fontsize_clock0em50), data["time_year"], font = font_clock0em50, fill = 0)
    draw_black.line((vline, padding+fontsize_clock, 870, padding+fontsize_clock), fill = 0) #horizontal line

    #Weather
    draw_black.text((vline+0.5*padding, 2*padding+fontsize_clock), str(data["precipitation"]) + "%", font = font_clock1em, fill = 0)
    draw_black.text((vline+0.5*padding+fontsize_clock+fontsize_clock0em50, 2*padding+fontsize_clock), "Regen-" , font = font_clock0em33, fill = 0)
    draw_black.text((vline+0.5*padding+fontsize_clock+fontsize_clock0em50, 2*padding+fontsize_clock+fontsize_clock0em33), "wahrschein-" , font = font_clock0em33, fill = 0)
    draw_black.text((vline+0.5*padding+fontsize_clock+fontsize_clock0em50, 2*padding+fontsize_clock+2*fontsize_clock0em33), "lichkeit" , font = font_clock0em33, fill = 0)
    draw_black.line((vline, 3*padding+fontsize_clock, 870, 3*padding+fontsize_clock), fill = 0) #horizontal line

    return 0

try:
    logging.info("epd7in5b_HD Demo")

    epd = epd7in5b_HD.EPD()

    while True:
        logging.info("Init and Clear")
        epd.init()
        epd.Clear() 
        result = getData()
        black, red = initBuffer()
        fillBuffer(result, black, red)
        epd.display(epd.getbuffer(black), epd.getbuffer(red))
        time.sleep(300) #300s=5min

        #logging.info("Goto Sleep...")
        #epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_HD.epdconfig.module_exit()
    exit()
