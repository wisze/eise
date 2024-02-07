import sys
# from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from skyfield import almanac
from skyfield.api import load, wgs84, N, E, W, S
from skyfield.api import position_of_radec, load_constellation_map
from skyfield.framelib import ecliptic_frame

# display = auto()
ikoon = Image.new("RGB",(800,480), (0,0,150))
draw = ImageDraw.Draw(ikoon)
draw.arc([(5,5),(475,475)],0,360,(255,0,0),3)

# Bepaal positie van de waarnemer
ams = wgs84.latlon(52.375 * N, 4.900 * E)
# ik = aarde + ams
print (ams.latitude, ams.longitude)

# Bepaal lokale tijd en bereken de sterrentijd (sideral time)
ts = load.timescale()
t = ts.now()
st = t.gast+ams.longitude.degrees/360*24
hoek_lentepunt = st/24*360
print ('tijd', t, hoek_lentepunt)
# Check, waar staat het lentepunt?
lentepunt = position_of_radec(0,0)
constellation_at = load_constellation_map()
print ('lentepunt staat in', constellation_at(lentepunt))

# Laad de baangegevens van de planeten, JPL ephemeris DE421
eph = load('de421.bsp')
aarde = eph['earth']
planets = {'Maan':      'Moon',
           'Mercurius': 'Mercury',
           'Venus':     'Venus',
           'Zon':       'Sun',
           'Mars':      'Mars',
           'Jupiter':   'Jupiter barycenter',
           'Saturnus':  'Saturn barycenter',
           'Uranus':    'Uranus barycenter',
           'Neptunus':  'Neptune barycenter'}

# Bereken posities van de planeten in het ecliptisch assenstelsel
for p in planets:
   planeetpositie = aarde.at(t).observe(eph[planets[p]])
   lat, lon, d = planeetpositie.frame_latlon(ecliptic_frame)
   azimut_equatoriaal = (hoek_lentepunt-lon.degrees)%360
   print (p, constellation_at(planeetpositie), lon.degrees, azimut_equatoriaal)
   # Teken de zon
   if p == 'Zon':
      draw.arc([(60,60),(420,420)],0,360,(0,0,100),40)

ikoon.save('ikoon.png')
# display.set_image(ikoon)
# display.show()
