#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_HD
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import urllib, json

logging.basicConfig(level=logging.DEBUG)

try:
    temperature_url = 'https://www.kaiserslautern.de/export/baeder/waschmuehle_temperature.json'
    response = urllib.urlopen(temperature_url)
    data = json.loads(response.read())
    logging.info(data)

except IOError as e:
    logging.info(e)

try:
    logging.info("epd7in5b_HD Demo")

    epd = epd7in5b_HD.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'LiberationMono-Regular.ttf'), 24)
    font36 = ImageFont.truetype(os.path.join(picdir, 'LiberationMono-Regular.ttf'), 36)

    # Drawing on the Vertical image
    logging.info("1.Drawing on the Horizontal image...")
    black = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    red = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_black = ImageDraw.Draw(black)
    draw_red = ImageDraw.Draw(red)
    draw_red.text((10, 0), 'Informationsdisplay Waschmühle', font = font36, fill = 0)
    draw_black.text((10, 30), 'Wassertemperatur: 23.5°C', font = font24, fill = 0)
    epd.display(epd.getbuffer(black), epd.getbuffer(red))
    time.sleep(5)

    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_HD.epdconfig.module_exit()
    exit()
