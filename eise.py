# from skyfield import api
import os
import sys
import time
# import traceback
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from skyfield import almanac
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from astropy import units
from waveshare_epd import epd2in13bc
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
from pytz import timezone

maxalt = 75.0
minimum_magnitude = 3.0

epd = epd2in13bc.EPD()
print("Init scherm")
epd.init()
# epd.Clear()
font12 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 12)
font18 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 18)
cmastro12 = ImageFont.truetype(os.path.join(libdir, 'cmastro5.ttf'), 12)
cmastro14 = ImageFont.truetype(os.path.join(libdir, 'cmastro5.ttf'), 14)
time.sleep(1)

HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
HRYimage    = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image
drawblack = ImageDraw.Draw(HBlackimage)
drawred   = ImageDraw.Draw(HRYimage)

ts = load.timescale()
ephem = load('de421.bsp')
cet = timezone('CET')

earth = ephem['earth']

amsterdam = Topos('52.3679 N', '4.8984 E')
amstercentric = earth + amsterdam

t0 = ts.now()
t1 = ts.tt_jd(t0.tt + 1)

# Toon windrichtingen en kloktijd
nu = t0.utc_datetime().astimezone(cet).time().strftime('%H:%M')
drawred.text(( epd.height*90/360-5, epd.width-20), 'o', font = font18, fill = 0)
drawred.text((epd.height*180/360-5, epd.width-20), 'z', font = font18, fill = 0)
drawred.text((epd.height*270/360-5, epd.width-20), 'w', font = font18, fill = 0)
drawred.text((epd.height-32,0), nu, font = font12, fill = 0)

# Teken helderste sterren in
print("Teken sterrenkaart")
with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)
df = df[df['magnitude'] <= minimum_magnitude]
bright_stars = Star.from_dataframe(df)
print bright_stars
astrometric = amstercentric.at(t0).observe(bright_stars)
alt, az, distance = astrometric.apparent().altaz()
for alti, azi, mag in zip(alt.degrees, az.degrees, df['magnitude']):
    if (alti > 0.0 and alti < maxalt):
    	print ("Hoogte %6.2f, azimuth %6.2f, helderheid %6.2f"%(alti, azi, mag))
        ix = epd.height*azi/360.0
        iy = epd.width*(maxalt-alti)/maxalt
        size = (minimum_magnitude - mag)/2.0;
        print((ix-size, iy-size, ix+size, iy+size))
        # drawblack.point((ix-size, iy-size), fill = 0)
        drawblack.ellipse((ix-size, iy-size, ix+size, iy+size), fill = 0)

# Teken planeten in
print("Teken planeten")
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
        ix = epd.height*az.to(units.deg).value/360.0
        iy = epd.width*(maxalt-alt.to(units.deg).value)/maxalt
        drawblack.text((ix, iy-5), symbols[p], font = cmastro14, fill = 0)
    else:
        f = almanac.risings_and_settings(ephem, ephem[planets[p]], amsterdam)
        t, y = almanac.find_discrete(t0, t1, f)
        for ti, yi in zip(t, y):
            trise = ti.utc_datetime().astimezone(cet).time()
            if yi:
                opkomst = trise.strftime('%H:%M')
                print('  Opkomst om ' + opkomst)
                drawred.text((2,irise*14), symbols[p], font = cmastro12, fill = 0)
                drawred.text((16,irise*14), opkomst, font = font12, fill = 0)
                irise = irise+1

maanverlicht  = int(100*(almanac.fraction_illuminated(ephem, 'Moon', t0)+0.05))
venusverlicht = int(100*(almanac.fraction_illuminated(ephem, 'Venus', t0)+0.05))
print('Maan '+str(maanverlicht)+'% verlicht')
print('Venus '+str(venusverlicht)+'% verlicht')
drawred.text((epd.height-36,14), symbols['Maan'], font = cmastro12, fill = 0)
drawred.text((epd.height-36,28), symbols['Venus'], font = cmastro12, fill = 0)
drawred.text((epd.height-24,14), str(maanverlicht)+'%', font = font12, fill = 0)
drawred.text((epd.height-24,28), str(venusverlicht)+'%', font = font12, fill = 0)

epd.Clear()
epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))

epd.sleep()

