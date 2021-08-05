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
from PIL import Image,ImageDraw,ImageFont
import urllib, json
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
logging.basicConfig(level=logging.DEBUG)


height = 528
width = 880
padding = 30
col1_padding_left = 15
col1_padding_top = 30
col2_padding_left = 30
col2_padding_top = 25
vmiddle = height/2
vline = 510

col1_fontsize = 264
col1_fontsize0em66 = int(col1_fontsize*0.66)
col1_fontsize0em33 = int(col1_fontsize*0.33-10)

col2_fontsize = 110
col2_fontsize0em66 = int(col2_fontsize*0.66)
col2_fontsize0em50 = int(col2_fontsize*0.50)
col2_fontsize0em33 = int(col2_fontsize*0.33-5)

col1_font1em = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), col1_fontsize)
col1_font0em33 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II.ttf'), col1_fontsize0em33)
col1_font0em66 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), col1_fontsize0em66)

font_small = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II.ttf'), 26)
font_weekday = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), 40)
col2_font1em = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), col2_fontsize)
col2_font0em66 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), col2_fontsize0em66)
col2_font0em50 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II_Bold.ttf'), col2_fontsize0em50)
col2_font0em33 = ImageFont.truetype(os.path.join(fontdir, 'Oslo_II.ttf'), col2_fontsize0em33)


def splitFloat(float_in):
    split = str(float_in).split(".") #split float into integer and fraction part
    out_int = int(split[0])
    out_frac = int(split[1])

    #round fraction part to 5 or 0
    if(out_frac <=2 ): 
        out_frac=0 
    elif(out_frac >2 and  out_frac<=7): 
        out_frac=5
    else :
        out_frac=0
        out_int += 1    
        
    return out_int, out_frac


def getData():
    logging.info("Retrieving Data...")
    #Sensordata
    try:
        temperature_url = 'https://www.kaiserslautern.de/export/baeder/waschmuehle_temperature.json'
        response = urllib.urlopen(temperature_url)
        data = json.loads(response.read())
        temperature_water = float(data['data']['external_temperature_1'])
        temperature_water_int, temperature_water_frac = splitFloat(temperature_water)
        temperature_air = float(data['data']['temperature'])
        temperature_air_int, temperature_air_frac = splitFloat(temperature_air)
        humidity = float(data['data']['humidity'])
        humidity_int, humidity_frac = splitFloat(humidity)
        sensor_error = False
    except ValueError:
        temperature_air = temperature_air_frac = temperature_air_int = temperature_water = temperature_water_frac = temperature_water_int = humidity = humidity_frac = humidity_int = None
        sensor_error = True
        logging.error("Decoding JSON Failed. URL: " + temperature_url)

    
    
    #date and time
    now = datetime.now()
    time_hours = now.strftime("%H")
    time_minutes = now.strftime("%M")
    time_year = now.strftime("%y")
    time_date = now.strftime("%d.%m.")
    time_weekday = now.strftime("%A")

    #weather 
    try:
        dwd_url = 'https://www.kaiserslautern.de/export/wetter/dwd_wetter_morlautern.json'
        response = urllib.urlopen(dwd_url)
        logging.debug(response)
        data = json.loads(response.read())
        precipitation = float(data['precipitation_perc'])
        precipitation_int, precipitation_frac = splitFloat(precipitation)
        weather_error = False
    except ValueError:
        precipitation = precipitation_frac = precipitation_int = None
        weather_error = True
        logging.error("Decoding JSON Failed. URL: " + dwd_url)

    result = {
        "temperature_water_int" : temperature_water_int,
        "temperature_water_frac" : temperature_water_frac,
        "temperature_air_int" : temperature_air_int,
        "temperature_air_frac" : temperature_air_frac,
        "humidity" : humidity,
        "humidity_int" : humidity_int,
        "humidity_frac" : humidity_frac,
        "sensor_error" : sensor_error,
        "time_hours" : time_hours,
        "time_minutes" : time_minutes,
        "time_year" : time_year,
        "time_date" : time_date,
        "time_weekday" : time_weekday,
        "precipitation" : precipitation,
        "precipitation_int" : precipitation_int,
        "precipitation_frac" : precipitation_frac,
        "weather_error" : weather_error
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
    if(data["sensor_error"] == False):
        draw_black.text((col1_padding_left, col1_padding_top), str(data["temperature_air_int"]).zfill(2), font = col1_font1em, fill = 0)
        draw_black.text((col1_padding_left+col1_fontsize, col1_padding_top), "." + str(data["temperature_air_frac"]) + u"°C", font = col1_font0em66, fill = 0)
        draw_black.text((col1_padding_left+col1_fontsize, col1_padding_top+col1_fontsize0em66-30), "Luft", font = col1_font0em33, fill = 0)

    draw_black.line((0, vmiddle, vline, vmiddle), fill = 0) # horizontal line
    if(data["sensor_error"] == False):
        draw_black.text((col1_padding_left, vmiddle+col1_padding_top), str(data["temperature_water_int"]).zfill(2), font = col1_font1em, fill = 0)
        draw_black.text((col1_padding_left+col1_fontsize, vmiddle+col1_padding_top), "." + str(data["temperature_water_frac"]) + u"°C", font = col1_font0em66, fill = 0)
        draw_black.text((col1_padding_left+col1_fontsize, vmiddle+col1_padding_top+col1_fontsize0em66-30), "Wasser", font = col1_font0em33, fill = 0)
    
    draw_black.line((vline, 0, vline, height), fill = 0) #vertical Line

    #Day
    #draw_black.rectangle((vline, 0, width, height*1/8), fill = 0)
    draw_black.text((vline+col2_padding_left, col2_padding_top), data["time_weekday"], font = font_weekday, fill = 0)
    draw_black.line((vline, height*1/8, width, height*1/8), fill = 0) #horizontal line
    
    #Date
    draw_black.text((vline+col2_padding_left, height*1/8+col2_padding_top), data["time_date"] + data["time_year"], font = col2_font1em, fill = 0)
    draw_black.line((vline, height*3/8, width, height*3/8), fill = 0) #horizontal line

    #Weather
    if(data["weather_error"] == False):
        draw_black.text((vline+col2_padding_left, height*3/8+col2_padding_top), str(data["precipitation_int"]).zfill(2) + "%", font = col2_font1em, fill = 0)
        draw_black.text((vline+col2_padding_left+1.5*col2_fontsize, height*3/8+col2_padding_top), "Regen- " , font = col2_font0em33, fill = 0)
        draw_black.text((vline+col2_padding_left+1.5*col2_fontsize, height*3/8+col2_padding_top+col2_fontsize0em33), "wahrschein- " , font = col2_font0em33, fill = 0)
        draw_black.text((vline+col2_padding_left+1.5*col2_fontsize, height*3/8+col2_padding_top+2*col2_fontsize0em33), "lichkeit" , font = col2_font0em33, fill = 0)
        
    draw_black.line((vline, height*5/8, width, height*5/8), fill = 0) #horizontal line

    if(data["sensor_error"] == False):
        draw_black.text((vline+col2_padding_left, height*5/8+col2_padding_top), str(data["humidity_int"]).zfill(2) + "%", font = col2_font1em, fill = 0)
        draw_black.text((vline+col2_padding_left+1.5*col2_fontsize, height*5/8+col2_padding_top), "Luft- " , font = col2_font0em33, fill = 0)
        draw_black.text((vline+col2_padding_left+1.5*col2_fontsize, height*5/8+col2_padding_top+col2_fontsize0em33), "feuchtig- " , font = col2_font0em33, fill = 0)
        draw_black.text((vline+col2_padding_left+1.5*col2_fontsize, height*5/8+col2_padding_top+2*col2_fontsize0em33), "keit" , font = col2_font0em33, fill = 0)


    draw_black.line((vline, height*7/8, width, height*7/8), fill = 0) #horizontal line
    draw_black.text((vline+col2_padding_left, height*7/8+col2_padding_top), "Zuletzt aktualisiert: "+ data["time_date"] + data["time_year"] +" " + data["time_hours"] + ":" + data["time_minutes"], font = font_small, fill = 0)

    return 0



try:
    logging.info("epd7in5b_HD Demo")

    epd = epd7in5b_HD.EPD()

    logging.info("Init and Clear")
    epd.init()
    epd.Clear() 
    result = getData()
    black, red = initBuffer()
    fillBuffer(result, black, red)
    epd.display(epd.getbuffer(black), epd.getbuffer(red))
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_HD.epdconfig.module_exit()
    exit()
