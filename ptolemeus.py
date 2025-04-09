import sys, math, time
# from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from skyfield import almanac
from skyfield.api import load, wgs84, N, E, W, S
from skyfield.api import position_of_radec, load_constellation_map
from skyfield.framelib import ecliptic_frame

# Verschillende konstanten
# Wat is een jaar?
tropischjaar  = 365.2421896 # Kalenderjaar. Geen constante, dit is de 2000.0 waarde
siderischjaar = 365.256363004 # Ongeveer 20 minuten langer dan tropisch jaar, ook 2000.0
tropischemaand  = 27.32158 # Tijd tussen doorgangen van de Maan door de ecliptica
siderischemaand = 27.32166 
synodischemaand = 29.53059 # Tijd tussen nieuwe manen
draconitischemaand = 27,21222 # Tijd tussen twee knopendoorgangen
# Waar staat de waarnemer?
lengte020 = 4.9 # Graden oosterlengte
tweepi    = 6.28

# Fonts
schwabacher = ImageFont.truetype("lib/yswab.otf",size=20)
astrologicus = ImageFont.truetype("lib/Astrologicus.ttf",size=40)

# Lijstje planeten, Uranus en Neptunus bestaan nog niet
planeten = {'Maan': 'Moon', 'Mercurius': 'Mercury', 'Venus': 'Venus',
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
      print (s,hoeks//1)
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

# Epicykel geeft de ware anomalie, de hoek van een planeet ten opzichte van het
# lentepunt gezien vanuit de Aarde, berekend met Ptolemaeaus epicykels.
#
# De deferent is de hoofdcirkel, de epicykel is de kleine cirkel daarop
# De eccenter is het middelpunt van de cirkel, de equant is het punt waaromheen
# het middelpunt van de epicykel op de deferent met constante hoeksnelheid beweegt.
# Aarde, eccenter en equant liggen op 1 lijn.
def epicykel(deferent,epicyckel,eccenter,equant):
   # Hoek vanuit de equans
   equansanomalie = (tijd-tijdperiapsis)/omlooptijd*tweepi
   equansx = deferent * cos(equansanomalie)
   equansy = deferent * sin(equansanomalie)
   # Hoek vanuit de Aarde
   wareanomalie = arctan(equansy/(equansx-2*equans))
   schijnbareanomalie = wareanomalie + lengteperiapsis
   return schijnbareanomalie

# De Zon en de Maan beschijven een cirkalbaan om de Aarde
def cirkelbaan(t,T):
   schijnbareanomalie = ( t / T ) % 360.0
   return schijnbareanomalie

# Keplerbaan geeft de ware anomalie, de hoek van een planeet ten opzichte van het
# lentepunt gezien vanuit de Zon.
def keplerbaan(tijd):
   return wareanomalie

# Metonische cyclus, 19 jaar komt overeen met 235 maanden
def meton(tijd):
   return metonfractie

# Saros periode, na een periode 223 maanden, ongeveer 18 jaar, herhalen eclipses
# 
# Een Saros serie is een reeks bijna gelijke eclipses
def saros(tijd):
   return sarosfractie

# Bepaal lokale tijd en lokale sterrentijd, om zomertijd ellende te voorkomen alles vanaf gm
nu = time.time() / 86400  # nu, in dagen
dagen = nu // 1 + 2440587 # dagen, juliaanse datum
tijd  = nu % 1 # Fractie van de dag
print('Epoch in dagen',nu)
print('JD', dagen)
print('GMT          ', int(24*tijd), int((24*60*tijd)%60), (24*3600*tijd)%60)

# Siderische tijd foezelfactor
epochsiderisch = 3.091 / 24.0
GMST = ( nu * siderischjaar/(siderischjaar-1.0) + epochsiderisch ) % 1
print('GMT siderisch',int(24*GMST), int((24*60*GMST)%60), (24*3600*GMST)%60)

# Lokale tijd en sterretijd in fracties van de dag
lokaletijd = ( nu + lengte020/360.0 ) % 1 # Correctie voor locatie NL
print('Lokale zonnetijd',int(24*lokaletijd), int((24*60*lokaletijd)%60), (24*3600*lokaletijd)%60)
LMST = ( ( nu + lengte020/360.0 ) * siderischjaar/(siderischjaar-1.0) + epochsiderisch ) % 1
print('Lokaal siderisch', int(24*LMST), int((24*60*LMST)%60), (24*3600*LMST)%60)

# Begin met tekenen
ikoon = Image.new("RGB",(480,800), (255,255,255))
sfeer_x = ikoon.width/2
sfeer_y = ikoon.height - ikoon.width/2
draw = ImageDraw.Draw(ikoon)

r = 38
teken_aarde(r)
r += 1
# Bereken posities van de planeten en teken de sfeer in
for p in planeten:
   azimut = 0.0
   # azimut = epicykel() + hoeklentepunt;
   # Teken de cirkel met planeet
   
   if (p == 'Zon'):
      azimut = cirkelbaan(tijd,siderischjaar) + LMST*360.0
      w = 36
   elif (p == 'Maan'):
      azimut = cirkelbaan(tijd,synodischemaand) + LMST*360.0
      w = 36
   else:
      w = 16
   r += w+1;
   teken_planeet(r,azimut,w,p)
# Teken de dierenriem
w = 36
r += w+1
teken_dierenriem(r,LMST*360,w)
   
ikoon.save('ptolemeus.png')
ikoon.show()
# ikoon_gedraaid = ikoon.rotate((270), expand=True,center=(ikoon.width/2,ikoon.height/2))
# display = auto()
# display.set_image(ikoon_gedraaid)
# display.show()
