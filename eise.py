# from skyfield import api
import os
import sys
import svgwrite
import time
# import traceback
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from skyfield import almanac
from skyfield.api import load
from skyfield.api import Topos
from astropy import units
from waveshare_epd import epd2in13bc
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
from pytz import timezone

drwwidth = 800
drwheight = 400
maxalt = 60.0

epd = epd2in13bc.EPD()
print("Init en Clear scherm")
epd.init()
epd.Clear()
dwg = svgwrite.Drawing('/var/www/html/sterrenhemel.svg', profile='tiny')
font12 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 12)
font18 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 18)
cmastro10 = ImageFont.truetype(os.path.join(libdir, 'cmastro5.ttf'), 14)
time.sleep(1)

HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
HRYimage    = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image
drawblack = ImageDraw.Draw(HBlackimage)
drawred   = ImageDraw.Draw(HRYimage)

ts = load.timescale()
ephem = load('de421.bsp')
cet = timezone('CET')

sun, moon, earth = ephem['sun'], ephem['moon'], ephem['earth']

amsterdam = Topos('52.3679 N', '4.8984 E')
amstercentric = earth + amsterdam

t0 = ts.now()
t1 = ts.tt_jd(t0.tt + 1)
nu = t0.utc_datetime().astimezone(cet).time().strftime('%H:%M')

dwg.add(dwg.line((  0, 90), (360, 90), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((  0,  0), (  0, 90), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((360,  0), (360, 90), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((  0,  0), (360,  0), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line(( 90, 88), ( 90, 92), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((180, 88), (180, 92), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((270, 88), (270, 92), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.text('o', insert=( 90.0, 105.0), fill='black'))
dwg.add(dwg.text('z', insert=(180.0, 105.0), fill='black'))
dwg.add(dwg.text('w', insert=(270.0, 105.0), fill='black'))

# print(epd.width, epd.height)
drawred.text(( epd.height*90/360-5, epd.width-20), 'o', font = font18, fill = 0)
drawred.text((epd.height*180/360-5, epd.width-20), 'z', font = font18, fill = 0)
drawred.text((epd.height*270/360-5, epd.width-20), 'w', font = font18, fill = 0)
drawblack.text((epd.height-32,0), nu, font = font12, fill = 0)

# planets = ['Mercury', 'Venus', 'Mars', 'Jupiter barycenter', 'Saturn barycenter', 'Neptune barycenter', 'Uranus barycenter']
planets = {'Zon':       'Sun',
           'Maan':      'Moon',
           'Mercurius': 'Mercury',
           'Venus':     'Venus',
           'Mars':      'Mars',
           'Jupiter':   'Jupiter barycenter',
           'Saturnus':  'Saturn barycenter',
           'Uranus':    'Uranus barycenter',
           'Neptunus':  'Neptune barycenter'}
symbols = {'Zon':       'S',
           'Maan':      'M',
           'Mercurius': '1',
           'Venus':     '2',
           'Mars':      '4',
           'Jupiter':   '5',
           'Saturnus':  '6',
           'Uranus':    '7',
           'Neptunus':  '8'}
irise = 0
for p in planets:
    print p

    # astrometric = earth.at(t0).observe(ephem[planets[p]])
    astrometric = amstercentric.at(t0).observe(ephem[planets[p]])
    ra, dec, distance = astrometric.radec()
    alt, az, distance = astrometric.apparent().altaz()

    print("  Declinatie: %6.2f Rechte klimming: %6.2f " % (dec.to(units.deg).value, ra.to(units.deg).value))
    if alt.to(units.deg) > 0.0:
        print("  Hoogte: %6.2f, Azimuth: %6.2f"% (alt.to(units.deg).value, az.to(units.deg).value))
        dwg.add(dwg.text(p[0], insert=(az.to(units.deg).value, 90.0-alt.to(units.deg).value), fill='black'))
        ix = epd.height*az.to(units.deg).value/360.0
        iy = epd.width*(maxalt-alt.to(units.deg).value)/maxalt
        drawblack.text((ix, iy-5), symbols[p], font = cmastro10, fill = 0)
    else:
        f = almanac.risings_and_settings(ephem, ephem[planets[p]], amsterdam)
        t, y = almanac.find_discrete(t0, t1, f)
        for ti, yi in zip(t, y):
            trise = ti.utc_datetime().astimezone(cet).time()
            if yi:
                opkomst = trise.strftime('%H:%M')
                print('  Opkomst om ' + opkomst)
                drawblack.text((2,irise*14), symbols[p], font = cmastro10, fill = 0)
                drawred.text((16,irise*14), opkomst, font = font12, fill = 0)
                irise = irise+1

maanverlicht  = int(100*(almanac.fraction_illuminated(ephem, 'Moon', t0)+0.05))
venusverlicht = int(100*(almanac.fraction_illuminated(ephem, 'Venus', t0)+0.05))
print('Maan '+str(maanverlicht)+'% verlicht')
print('Venus '+str(venusverlicht)+'% verlicht')
drawblack.text((epd.height-36,14), symbols['Maan'], font = cmastro10, fill = 0)
drawblack.text((epd.height-36,28), symbols['Venus'], font = cmastro10, fill = 0)
drawred.text((epd.height-24,14), str(maanverlicht)+'%', font = font12, fill = 0)
drawred.text((epd.height-24,28), str(venusverlicht)+'%', font = font12, fill = 0)

epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
dwg.save()

# epd.init()
# epd.Clear()
epd.sleep()

