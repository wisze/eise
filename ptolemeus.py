import sys
import math
# from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from skyfield import almanac
from skyfield.api import load, wgs84, N, E, W, S
from skyfield.api import position_of_radec, load_constellation_map
from skyfield.framelib import ecliptic_frame

# Fonts
schwabacher = ImageFont.truetype("lib/OfenbacherSchwabCAT.ttf",size=20)
astrologicus = ImageFont.truetype("lib/Astrologicus.ttf",size=40)
# Lijstje planeten, Uranus en Neptunus bestaan nog niet
planets = {'Maan': 'Moon', 'Mercurius': 'Mercury', 'Venus': 'Venus',
           'Zon': 'Sun', 'Mars': 'Mars',
           'Jupiter': 'Jupiter barycenter', 'Saturnus': 'Saturn barycenter'}
# Sterrenbeelden vanaf lentepunt met icoon uit Astrologicus font
sterrenbeelden = {'Ram':'A','Stier':'B','Tweelingen':'C','Krab':'D',
                  'Leeuw':'E','Maagd':'F','Weegschaal':'G','Kreeft':'H',
                  'Boogschutter':'I','Steenbok':'J','Waterman':'K','Vissen':'L'} 

def teken_aarde(straal):
   draw.ellipse([(sfeer_x-straal,sfeer_y-straal),
                 (sfeer_x+straal,sfeer_y+straal)],(0,250,0),(0,0,0),1)

def teken_planeet(straal,phi,d,naam):
   x = (straal-d/2)*math.sin(math.radians(phi))
   y = (straal-d/2)*math.cos(math.radians(phi))
   lcenter = 40 # grootte van ee plaatje voor een planeet
   sfeer = Image.new("RGBA", (lcenter*2,lcenter*2), (0, 0, 0, 0))
   label = ImageDraw.Draw(sfeer)
   draw.arc([(sfeer_x-straal,sfeer_y-straal),
             (sfeer_x+straal,sfeer_y+straal)],0,360,(0,0,250),d)
   label.ellipse([(lcenter-d/2,lcenter-d/2),
                  (lcenter+d/2,lcenter+d/2)],(250,250,100),(0,0,0),1)
   sfeer_gedraaid = sfeer.rotate((0.0-phi),resample=Image.BILINEAR,
                                 expand=False,center=(lcenter,lcenter))
   mask = sfeer_gedraaid.split()[3]
   ikoon.paste(sfeer_gedraaid,(int(sfeer_x+x-lcenter+0.5),
                               int(sfeer_y-y-lcenter+0.5)),mask)
   teken_tekst(straal,phi,d,naam)

def teken_tekst(straal,hoek,d,tekst):
   lbox = 20 # grootte van plaatje van een letter
   omtrek  = 2.0*3.14159*straal # omtrek in pixels van de basis van de tekst, ongeveer
   h = hoek + 360*1.4*d/omtrek
   for l in tekst:
      x = (straal-d/2)*math.sin(math.radians(h))
      y = (straal-d/2)*math.cos(math.radians(h))
      lbeeld = Image.new("RGBA", (lbox,lbox), (0, 0, 0, 0))
      letter = ImageDraw.Draw(lbeeld)
      letter.text((lbox/2,lbox/2), l, anchor="mm", font=schwabacher)
      lt = letter.textlength(l,schwabacher)
      lbeeld_gedraaid = lbeeld.rotate(-h,resample=Image.BILINEAR,
                                      expand=False,center=(lbox/2,lbox/2))
      mask = lbeeld_gedraaid.split()[3]
      ikoon.paste(lbeeld_gedraaid,(int(sfeer_x+x-lbox/2),
                                   int(sfeer_y-y-lbox/2)),mask)
      h += 360.0*1.2*lt/omtrek
  
def teken_dierenriem(straal,phi,d):
   sb = 100 # 100 pixels voor sterrenbeeld
   isterrenbeeld = 1
   draw.arc([(sfeer_x-straal,sfeer_y-straal),
             (sfeer_x+straal,sfeer_y+straal)],0,360,(100,100,250),d)
   for s in sterrenbeelden:
      hoeks = phi - isterrenbeeld*30.0
      x = (straal-d/2-4)*math.sin(math.radians(hoeks))
      y = (straal-d/2-4)*math.cos(math.radians(hoeks))
      print (s,hoeks,x,y)
      sterrenbeeld = Image.new("RGBA", (sb,sb), (0, 0, 0, 0))
      teken = ImageDraw.Draw(sterrenbeeld)
      teken.text((sb/2,sb/2), sterrenbeelden[s],
                 anchor="mm", fill=(0,0,0), font=astrologicus)
      sterrenbeeld_gedraaid = sterrenbeeld.rotate((0.0-hoeks),resample=Image.BILINEAR,
                                                  expand=False,center=(sb/2,sb/2))
      mask = sterrenbeeld_gedraaid.split()[3]
      ikoon.paste(sterrenbeeld_gedraaid,(int(sfeer_x+x-sb/2),
                                         int(sfeer_y-y-sb/2)),mask)
      isterrenbeeld += 1

ikoon = Image.new("RGB",(480,800), (255,255,255))
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

r = 38
teken_aarde(r)
r += 1
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
      w = 16
   r += w+1;
   teken_planeet(r,azimut_equatoriaal,w,p)
w = 35
r += w+1
teken_dierenriem(r,hoek_lentepunt,w)
   
ikoon.save('ptolemeus.png')
ikoon.show()
ikoon_gedraaid = ikoon.rotate((270), expand=True,center=(ikoon.width/2,ikoon.height/2))
# display = auto()
# display.set_image(ikoon_gedraaid)
# display.show()
