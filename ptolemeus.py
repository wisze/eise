import sys
import math
# from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from skyfield import almanac
from skyfield.api import load, wgs84, N, E, W, S
from skyfield.api import position_of_radec, load_constellation_map
from skyfield.framelib import ecliptic_frame

def teken_planeet(afstand,phi,d,naam):
   x = (afstand-d/2)*math.sin(math.radians(phi))
   y = (afstand-d/2)*math.cos(math.radians(phi))
   print ("   Positie",x,y)
   lcenter = 100
   sfeer = Image.new("RGBA", (lcenter*2,lcenter*2), (0, 0, 0, 0))
   label = ImageDraw.Draw(sfeer)
   draw.arc([(sfeer_x-afstand,sfeer_y-afstand),(sfeer_x+afstand,sfeer_y+afstand)],0,360,(50,50,250),d)
   label.ellipse([(lcenter-d/2,lcenter-d/2),(lcenter+d/2,lcenter+d/2)],(250,250,100),(0,0,0),1)
   label.text((lcenter+d/2,lcenter), naam, anchor="lm", font=schwabacher)
   sfeer_gedraaid = sfeer.rotate((0.0-phi),resample=Image.BILINEAR,expand=False,center=(lcenter,lcenter))
   # sfeer_gedraaid.show()
   mask = sfeer_gedraaid.split()[3]
   ikoon.paste(sfeer_gedraaid,(int(sfeer_x+x-lcenter+0.5),int(sfeer_y-y-lcenter+0.5)),mask)

def teken_zodiac(afstand,phi):

schwabacher = ImageFont.truetype("lib/OfenbacherSchwabCAT.ttf",size=14)
ikoon = Image.new("RGB",(480,800), (250,250,150))
sfeer_x = ikoon.width/2
sfeer_y = ikoon.height - ikoon.width/2
draw = ImageDraw.Draw(ikoon)

# Bepaal positie van de waarnemer
ams = wgs84.latlon(52.375 * N, 4.900 * E)
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
           'Saturnus':  'Saturn barycenter'}

r = 50
# Bereken posities van de planeten in het ecliptisch assenstelsel
for p in planets:
   planeetpositie = aarde.at(t).observe(eph[planets[p]])
   lat, lon, d = planeetpositie.frame_latlon(ecliptic_frame)
   azimut_equatoriaal = (hoek_lentepunt-lon.degrees)%360
   print (p, constellation_at(planeetpositie), lon.degrees, azimut_equatoriaal)
   # Teken de cirkel met planeet
   if (p == 'Zon' or p == 'Maan'):
      w = 35
   else:
      w = 15
   r += w+2;
   teken_planeet(r,azimut_equatoriaal,w,p)

ikoon.save('ptolemeus.png')
ikoon.show()
ikoon_gedraaid = ikoon.rotate((270), expand=True,center=(ikoon.width/2,ikoon.height/2))
# display = auto()
# display.set_image(ikoon_gedraaid)
# display.show()
