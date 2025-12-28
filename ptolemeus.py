import sys, math, time, csv
# from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from skyfield import almanac
from skyfield.api import load, wgs84, N, E, W, S
from skyfield.api import position_of_radec, load_constellation_map
from skyfield.framelib import ecliptic_frame

# Verschillende konstanten voor jaar en maand
# tropischjaar  = 365.2421896 # Kalenderjaar. Geen constante, dit is de 2000.0 waarde
siderischjaar = 365.256363004 # Ongeveer 20 minuten langer dan tropisch jaar, ook 2000.0
# tropischemaand  = 27.32158 # Tijd tussen doorgangen van de Maan door de ecliptica
# siderischemaand = 27.32166 
synodischemaand = 29.53059 # Tijd tussen nieuwe manen
# draconitischemaand = 27,21222 # Tijd tussen twee knopendoorgangen
ashelling = 23.45 # Hoek tussen de rotatieas en de normaal op het baanvlak (de ecliptica)
# Waar staat de waarnemer?
lengte020 = 4.9 # Graden oosterlengte
tweepi    = 6.28318530718

# Lees baanelementen uit csv
planeet = []
element = {}
with open('orbits.csv', 'r') as orbitfile:
    csv_reader = csv.DictReader(orbitfile)
    for orbit in csv_reader:
        naam = orbit['naam'].strip()
        planeet.append(naam)
        element[naam] = {}
        element[naam]['a'] = float(orbit['a'])
        element[naam]['b'] = float(orbit['b'])
        element[naam]['e'] = float(orbit['e'])
        element[naam]['T'] = float(orbit['T'])
        element[naam]['lengteperi'] = float(orbit['l_peri'])
        element[naam]['epochperi']  = float(orbit['t_peri'])

# Fonts
schwabacher   = ImageFont.truetype("lib/yswab.otf",size=20)
schwabacher28 = ImageFont.truetype("lib/yswab.otf",size=28)
kapitaal      = ImageFont.truetype("lib/Yinit.otf",size=80)
astrologicus  = ImageFont.truetype("lib/Astrologicus.ttf",size=40)

# Sterrenbeelden vanaf lentepunt met icoon uit Astrologicus font
sterrenbeelden = {'Ram':'A','Stier':'B','Tweelingen':'C','Krab':'D',
                  'Leeuw':'E','Maagd':'F','Weegschaal':'G','Kreeft':'H',
                  'Boogschutter':'I','Steenbok':'J','Waterman':'K','Vissen':'L'} 

def teken_aarde(straal):
   draw.ellipse([(sfeer_x-straal,sfeer_y-straal),
                 (sfeer_x+straal,sfeer_y+straal)],(0,250,0),(0,0,0),1)

def teken_planeet(straal,lengte,sidderisch,d,naam):
   phi = sidderisch - lengte
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

# Teken de dierenriem. Afstand tussen sterrenbeelden is 30 graden.
# Alle sterrenbeelden worden gedraaid en in de bovenste sfeer getekend.
def teken_dierenriem(straal,phi,d):
   sb = 100 # 100 pixels voor sterrenbeeld
   isterrenbeeld = 1
   draw.arc([(sfeer_x-straal,sfeer_y-straal),
             (sfeer_x+straal,sfeer_y+straal)],0,360,(100,100,250),d)
   for s in sterrenbeelden:
      hoeks = phi - isterrenbeeld*30.0
      x = (straal-d/2-4)*math.sin(math.radians(hoeks))
      y = (straal-d/2-4)*math.cos(math.radians(hoeks))
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

# Teken de beschrijving bovenaan aan de pagina.
def beschrijving(tekst):
    regellengte = 20
    woorden = tekst.split()
    zin = ''
    regelnummer = 0
    tekstblok = Image.new("RGBA", (400,400), (0, 0, 0, 0))
    for woord in woorden:
        zin = zin + woord + ' '
        if (len(zin) > regellengte):
            print (len(zin),zin)
            regel = ImageDraw.Draw(tekstblok)
            regel.text((20, 80+regelnummer*24), zin, anchor="ls", fill=(0,0,0), font=schwabacher28)
            zin = ''
            regelnummer += 1
    mask = tekstblok.split()[3]
    ikoon.paste(tekstblok,(0,0,400,400),mask)
   
# Ptolemeus geeft de ecliptische lengte, de hoek van een planeet ten opzichte van het
# lentepunt gezien vanuit de Aarde, berekend met Ptolemaeaus epicykels.
#
# De deferent is het middelpunt van de cirkel. Deferent, equans en de Aarde liggen op 1 lijn.
# Equans en Aarde lige op eccentriciteit*straal afstand van de deferent.
# De planeet beweegt met constante hoeksnelheid gezien vanuit de de equans.
def epicykel(tijd,omlooptijd,a,b,excentriciteit,lengteperiapsis,tijdperiapsis,epicykelstraal,epicykellengte):
    straal = (a+b)/2.0
    deferent = straal * excentriciteit
    # Anomalie gezien van de equans is een lineaire functie van de tijd
    ### toepassing van de lengte van de periapsis klopt nog steeds niet helemaal ###
    defanomalie = ( (tijd-tijdperiapsis)/omlooptijd + lengteperiapsis/360.0 ) * tweepi
    defx = straal*math.cos(defanomalie)-deferent
    defy = straal*math.sin(defanomalie)
    print ('   deferent anomalie',defanomalie%360.0)
    print ('   epicykel anomalie',epicykellengte%360.0)
    # De epicykel. De cirkel op de cirkel. Berekend buiten deze functie
    planeetx = defx + epicykelstraal*math.cos(epicykellengte/360.0*tweepi)
    planeety = defy + epicykelstraal*math.sin(epicykellengte/360.0*tweepi)
    # Hoek vanuit de Aarde
    wareanomalie = math.atan2(planeety, planeetx)/tweepi*360.0
    print ('   ware anomalie',wareanomalie%360.0)
    # ecliptischelengte = wareanomalie + lengteperiapsis
    ecliptischelengte = wareanomalie % 360.0
    print ('   ecliptische lengte',ecliptischelengte)
    return ecliptischelengte

# De Zon en de Maan beschijven een cirkelbaan om de Aarde
# De equans wordt hier buiten beschouwing gelaten
def cirkelbaan(tijd,omlooptijd,a,b,excentriciteit,lengteperiapsis,tijdperiapsis):
    straal = (a+b)/2.0
    deferent = straal * excentriciteit
    # Anomalie gezien van de equans is een lineaire functie van de tijd
    defanomalie = (tijd-tijdperiapsis)/omlooptijd*tweepi
    defx = straal*math.cos(defanomalie)-deferent
    defy = straal*math.sin(defanomalie)
    # Hoek vanuit de Aarde
    wareanomalie = math.atan2(defy, defx)/tweepi*360.0
    print('   ware anmomalie',wareanomalie)
    ecliptischelengte = (wareanomalie+lengteperiapsis )%360
    print('   ecliptische lengte',ecliptischelengte)
    return ecliptischelengte

# Metonische cyclus, 19 jaar komt overeen met 235 maanden
# Geeft het gouden getal 
def meton(tijd):
   return metonfractie

# Een Saros serie is een reeks bijna gelijke eclipses.
# Na een periode 223 maanden, ongeveer 18 jaar, herhalen eclipses.
# 6585,3 dagen
def saros(tijd):
   return sarosfractie

# Bepaal lokale tijd en lokale sterrentijd, om zomertijd ellende te voorkomen alles vanaf gm
nu = time.time() / 86400  # nu, in dagen
jd = nu + 2440587.45833 # dagen, juliaanse datum
tijd  = nu % 1 # Fractie van de dag
print('Epoch in dagen',nu)
print('JD', jd)
print('GMT          ', int(24*tijd), int((24*60*tijd)%60), (24*3600*tijd)%60)

# Op 1/1/1970 was GMST 6 40 55 = 6,681944444
epochsiderisch = 6.681944444 / 24.0
GMST = ( nu * (siderischjaar+1)/siderischjaar + epochsiderisch ) % 1
print('GMT siderisch',int(24*GMST), int((24*60*GMST)%60), (24*3600*GMST)%60)

# Lokale tijd en sterretijd in fracties van de dag
lokaletijd = ( nu + lengte020/360.0 ) % 1 # Correctie voor locatie NL
print('Lokale zonnetijd',int(24*lokaletijd), int((24*60*lokaletijd)%60), (24*3600*lokaletijd)%60)
LMST = ( ( nu + lengte020/360.0 ) * (siderischjaar+1)/siderischjaar + epochsiderisch ) % 1
print('Lokaal siderisch', int(24*LMST), int((24*60*LMST)%60), (24*3600*LMST)%60)

# Begin met tekenen
ikoon = Image.new("RGB",(480,800), (255,255,255))
sfeer_x = ikoon.width/2
sfeer_y = ikoon.height - ikoon.width/2
draw = ImageDraw.Draw(ikoon)

r = 38
teken_aarde(r)
r += 1

# Eerst hebben we de lengte en afstand van de Zon van de Aarde nodig
print ('Zon')
epilengte = cirkelbaan(jd,element['Zon']['T'],
                        element['Zon']['a'],element['Zon']['b'],element['Zon']['e'],
                        element['Zon']['epochperi'],element['Zon']['lengteperi'])
epistraal = (element['Zon']['a']+element['Zon']['b'])/2.0
# Bereken posities van de planeten en teken de sfeer in
for naam in planeet:
   lengte = 0.0
   print (naam)
         
   if (naam == 'Zon'):
       lengte = epilengte
       w = 36
   elif (naam == 'Maan'):
       lengte = cirkelbaan(jd,synodischemaand,
                           element[naam]['a'],element[naam]['b'],element[naam]['e'],
                           element[naam]['lengteperi'],element[naam]['epochperi'])
       w = 36
   else:
       lengte = epicykel(jd,element[naam]['T'],
                         element[naam]['a'],element[naam]['b'],element[naam]['e'],
                         element[naam]['lengteperi'],element[naam]['epochperi'],
                         epistraal,epilengte)
       w = 16
   r += w+1;
   teken_planeet(r,lengte,LMST*360,w,naam)

# Teken de dierenriem
w = 36
r += w+1
teken_dierenriem(r,LMST*360,w)
beschrijving("De planeten volgens Ptolemeus. Jupiter is retrograad. Het is tijd voor vespers.")

ikoon.save('ptolemeus.png')
ikoon.show()
# ikoon_gedraaid = ikoon.rotate((270), expand=True,center=(ikoon.width/2,ikoon.height/2))
# display = auto()
# display.set_image(ikoon_gedraaid)
# display.show()
