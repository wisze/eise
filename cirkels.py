import sys, math, time, csv
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone

# Verschillende konstanten voor jaar en maand
tropischjaar  = 365.2421896 # Kalenderjaar. Geen constante, dit is de 2000.0 waarde
siderischjaar = 365.256363004 # Ongeveer 20 minuten langer dan tropisch jaar, ook 2000.0
tropischemaand  = 27.32158 # Tijd tussen doorgangen van de Maan door de ecliptica
siderischemaand = 27.32166 
synodischemaand = 29.53059 # Tijd tussen nieuwe manen
draconitischemaand = 27,21222 # Tijd tussen twee knopendoorgangen
ashelling = 23.45 # Hoek tussen de rotatieas en de normaal op het baanvlak (de ecliptica)
# Waar staat de waarnemer?
lengte020 = 4.9 # Graden oosterlengte
tweepi    = 6.28

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

       
# Epicykel geeft de ware anomalie, de hoek van een planeet ten opzichte van het
# lentepunt gezien vanuit de Aarde, berekend met Ptolemaeaus epicykels.
#
# De deferent is het middelpunt van de cirkelbaan
# De planeet beweegt met constante hoeksnelheid rond de equans
# Aarde, deferent en equans liggen op 1 lijn.
def epicykel(tijd,omlooptijd,a,b,excentriciteit,lengteperiapsis,tijdperiapsis,epicykelstraal,epicykellengte):
    straal = (a+b)/2.0
    # straalaarde = (149476014.0805783 + 149454602.05227306) / 2.0
    schaal = 400 / (straal+epicykelstraal) 
    deferent = straal * excentriciteit
    equans = 2 * deferent
    # Teken de deferent, equans en middelpunt
    draw.ellipse([(middenx-straal*schaal,middeny-straal*schaal),
                  (middenx+straal*schaal,middeny+straal*schaal)],outline=(0,0,0),fill=(250,200,200),width=1)
    draw.point([(middenx,middeny),(middenx,middeny-deferent*schaal)], fill=(0,0,0))
    draw.point([(middenx,middeny),(middenx,middeny-deferent*schaal)], fill=(0,0,0))
    draw.text((middenx,middeny-deferent*schaal), 'Equans',anchor='lm',fill=(0,0,0))
    draw.text((middenx,middeny+deferent*schaal), 'Aarde',anchor='lm',fill=(0,0,0))
    # Anomalie gezien van de equans is een lineaire functie van de tijd
    equansanomalie = (tijd-tijdperiapsis)/omlooptijd*tweepi
    print ('   tijd', tijd)
    print ('   tijd sinds periapsis',(tijd-tijdperiapsis))
    print ('   anomalie van de equans',equansanomalie/tweepi*180.0)
    defx = straal * math.cos(equansanomalie) - deferent
    defy = straal * math.sin(equansanomalie)
    print ('   x',defx)
    print ('   y',defy)
    # De epicykel, de cirkel op de cirkel
    # epianomalie = (tijd)/siderischjaar*tweepi % tweepi
    # print ('   anomalie van de epicykel',epianomalie/tweepi*180.0)
    # straalaarde = (149476014.0805783 + 149454602.05227306) / 2.0
    planeetx = defx + epicykelstraal * math.cos(epicykellengte/360.0*tweepi)
    planeety = defy + epicykelstraal * math.sin(epicykellengte/360.0*tweepi)
    # Hoek vanuit de Aarde
    wareanomalie = math.atan2(planeety, planeetx) / tweepi * 180.0
    print ('   ware anomalie',wareanomalie)
    ecliptischelengte = wareanomalie + lengteperiapsis
    print ('   ecliptische lengte',ecliptischelengte)
    draw.ellipse([(middenx+(defx-epicykelstraal)*schaal,middeny+(defy-epicykelstraal)*schaal),
                  (middenx+(defx+epicykelstraal)*schaal,middeny+(defy+epicykelstraal)*schaal)],
                   outline=(0,0,0),fill=(200,200,250),width=1)
    draw.line([(middenx,middeny+(deferent*schaal)),
               (middenx+defx*schaal,middeny+defy*schaal)],fill=(0,0,0),width=1)
    draw.line([(middenx+defx*schaal,middeny+defy*schaal),
               (middenx+planeetx*schaal,middeny+planeety*schaal)],
                fill=(0,0,0),width=1)
    draw.text((middenx+planeetx*schaal,middeny+planeety*schaal),naam,anchor='lm',fill=(0,0,0))
    return ecliptischelengte

# De Zon en de Maan beschijven een cirkelbaan om de Aarde
# De equans wordt hier buiten beschouwing gelaten
def cirkelbaan(tijd,omlooptijd,a,b,excentriciteit,lengteperiapsis,tijdperiapsis):
    straal = (a+b)/2.0
    deferent = straal * excentriciteit
    # Anomalie gezien van de equans is een lineaire functie van de tijd
    equansanomalie = (tijd-tijdperiapsis)/omlooptijd*tweepi
    equansx = straal*math.cos(equansanomalie)-deferent
    equansy = straal*math.sin(equansanomalie)
    # Hoek vanuit de Aarde
    wareanomalie = math.atan2(equansy, equansx)/tweepi*360.0
    # wareanomalie = ((tijd-tijdperiapsis)/omlooptijd)*360.0
    print('   ware anmomalie',wareanomalie)
    ecliptischelengte = (wareanomalie+lengteperiapsis )%360
    print('   ecliptische lengte',ecliptischelengte)
    return ecliptischelengte

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

# Bereken de offset door de Aarde
epilengte = cirkelbaan(jd,element['Zon']['T'],
                        element['Zon']['a'],element['Zon']['b'],element['Zon']['e'],
                        element['Zon']['epochperi'],element['Zon']['lengteperi'])
epistraal = (element['Zon']['a']+element['Zon']['b'])/2.0
# Bereken posities van de planeten
for naam in planeet:
   # Begin met tekenen
   diagram = Image.new("RGB",(800,800), (255,255,255))
   middenx = diagram.width/2
   middeny = diagram.height - diagram.width/2
   draw = ImageDraw.Draw(diagram)
   
   lengte = 0.0
   print (naam)
         
   if (naam == 'Zon'):
       lengte = cirkelbaan(jd,element[naam]['T'],
                           element[naam]['a'],element[naam]['b'],element[naam]['e'],
                           element[naam]['lengteperi'],element[naam]['epochperi'])
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
       
       filenaam = naam+'.png'
       diagram.save(filenaam)


