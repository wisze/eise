import sys, math, time, csv
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
# from skyfield import almanac
# from skyfield.api import load, wgs84, N, E, W, S
# from skyfield.api import position_of_radec, load_constellation_map
# from skyfield.framelib import ecliptic_frame

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
planeet = {}
ip = 0
with open('orbits.csv', 'r') as orbitfile:
    csv_reader = csv.DictReader(orbitfile)
    for orbit in csv_reader:
       planeet[ip] = {}
       planeet[ip]['naam'] = orbit['naam'].strip()
       planeet[ip]['a'] = float(orbit['a'])
       planeet[ip]['e'] = float(orbit['e'])
       planeet[ip]['T'] = float(orbit['T'])
       planeet[ip]['lengteperi'] = float(orbit['l_peri'])
       planeet[ip]['epochperi']  = float(orbit['t_peri'])
       ip += 1
print(ip,' planeten in orbit file')
       
# Epicykel geeft de ware anomalie, de hoek van een planeet ten opzichte van het
# lentepunt gezien vanuit de Aarde, berekend met Ptolemaeaus epicykels.
#
# De deferent is het middelpunt van de cirkelbaan
# De planeet beweegt met constante hoeksnelheid rond de equans
# Aarde, deferent en equans liggen op 1 lijn.
def epicykel(tijd,omlooptijd,straal,excentriciteit,lengteperiapsis,tijdperiapsis):
    schaal = 250 / straal  
    deferent = straal * excentriciteit
    equans = 2 * deferent
    # Teken de deferent, equans en middelpunt
    draw.ellipse([(middenx-straal*schaal,middeny-straal*schaal),
                  (middenx+straal*schaal,middeny+straal*schaal)],outline=(0,0,0),fill=(250,200,200),width=1)
    draw.point([(middenx,middeny),(middenx,middeny-deferent*schaal)], fill=(0,0,0))
    draw.point([(middenx,middeny),(middenx,middeny-deferent*schaal)], fill=(0,0,0))
    draw.text((middenx,middeny-deferent*schaal), 'Equans',anchor='ml',fill=(0,0,0))
    draw.text((middenx,middeny+deferent*schaal), 'Aarde',anchor='ml',fill=(0,0,0))
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
    epianomalie = (tijd)/siderischjaar*tweepi % tweepi
    print ('   anomalie van de epicykel',epianomalie/tweepi*180.0)
    straalaarde = (149476014.0805783 + 149454602.05227306) / 2.0
    planeetx = defx - straalaarde * math.cos(epianomalie)
    planeety = defy - straalaarde * math.sin(epianomalie)
    # Hoek vanuit de Aarde
    wareanomalie = math.atan2(defy, defx) / tweepi * 180.0
    print ('   ware anomalie',wareanomalie)
    schijnbareanomalie = wareanomalie + lengteperiapsis
    print ('   schijnbare anomalie',schijnbareanomalie)
    draw.ellipse([(middenx+(defx-straalaarde)*schaal,middeny+(defy-straalaarde)*schaal),
                  (middenx+(defx+straalaarde)*schaal,middeny+(defy+straalaarde)*schaal)],
                   outline=(0,0,0),fill=(200,200,250),width=1)
    draw.line([(middenx,middeny+(deferent*schaal)),
               (middenx+defx*schaal,middeny+defy*schaal)],fill=(0,0,0),width=1)
    draw.line([(middenx+defx*schaal,middeny+defy*schaal),
               (middenx+planeetx*schaal,middeny+planeety*schaal)],
                fill=(0,0,0),width=1)
    draw.text((middenx+planeetx*schaal,middeny+planeety*schaal),naam,anchor='ml',fill=(0,0,0))
    return schijnbareanomalie

# Bepaal lokale tijd en lokale sterrentijd, om zomertijd ellende te voorkomen alles vanaf gm
nu = time.time() / 86400  # nu, in dagen
juliaansedag = nu + 2440587.45833 # dagen, juliaanse datum
tijd  = nu % 1 # Fractie van de dag
print('Epoch in dagen',nu)
print('JD', juliaansedag)
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

# De straal van de baan van de Zon moet eigenlijk netjes uit de baanelementen gehaald worden
straalaarde = (149476014.0805783 + 149454602.05227306) / 2.0
# Bereken posities van de planeten en teken de sfeer in
for ip in planeet:
   # Begin met tekenen
   diagram = Image.new("RGB",(800,800), (255,255,255))
   middenx = diagram.width/2
   middeny = diagram.height - diagram.width/2
   draw = ImageDraw.Draw(diagram)

   lengte = 0.0
   # Teken de cirkel met planeet
   naam = planeet[ip]['naam']
         
   if (naam == 'Zon'):
       # lengte = cirkelbaan(nu,siderischjaar) + LMST*360.0
       lengte = lokaletijd*360.0-180.0
       print('Zon ecliptische lengte',lengte)
   elif (naam == 'Maan'):
       # lengte = cirkelbaan(nu,synodischemaand) + LMST*360.0 - 180.0
       print('Maan ecliptisce lengte',lengte)
   else:
       print(naam)
       lengte = epicykel(juliaansedag,
                         planeet[ip]['T'],planeet[ip]['a'],
                         planeet[ip]['e'],planeet[ip]['lengteperi'],
                         planeet[ip]['epochperi']) + LMST*360.0
       print(naam,'ecliptische lengte', lengte)
       filenaam = naam+'.png'
       diagram.save(filenaam)
       # diagram.show()

