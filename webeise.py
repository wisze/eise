from skyfield import almanac
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from astropy import units
from datetime import datetime
from pytz import timezone
import drawSvg as draw
import numpy as np
import math

# maxalt = 60.0
magnitude = 3.0
radius = 300
margin=50
fontsize=14
d = draw.Drawing(2*radius+margin, 2*radius+margin, origin='center', displayInline=False)
# Draw the horizon circle
d.append(draw.Circle(0, 0, radius, fill='lightgrey', stroke_width=2, stroke='black'))

ts = load.timescale()
ephem = load('de421.bsp')
cet = timezone('CET')

sun, moon, earth = ephem['sun'], ephem['moon'], ephem['earth']

amsterdam = Topos('52.3679 N', '4.8984 E')
amstercentric = earth + amsterdam

t0 = ts.now()
t1 = ts.tt_jd(t0.tt + 1)
nu = t0.utc_datetime().astimezone(cet).time().strftime('%H:%M')

# Teken helderste sterren in
print("Teken sterrenkaart")
with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)
df = df[df['magnitude'] <= magnitude]
bright_stars = Star.from_dataframe(df)
astrometric = amstercentric.at(t0).observe(bright_stars)
alt, az, distance = astrometric.apparent().altaz()
for alti, azi, mag in zip(alt.degrees, az.degrees, df['magnitude']):
    if (alti > 0.0):
        print ("hoogte: %6.2f, azimuth: %6.2f"%(alti, azi))
        ix = radius*(90.0-alti)/90.0*math.sin(np.deg2rad(-azi))
        iy = radius*(90.0-alti)/90.0*math.cos(np.deg2rad(-azi))
        d.append(draw.Circle(ix, iy, magnitude-mag,
            fill='white', stroke_width=0.8, stroke='black'))

# Teken planeten in
planets = {'☉': 'Sun',
           '☾': 'Moon',
           '☿': 'Mercury',
           '♀': 'Venus',
           '♂': 'Mars',
           '♃': 'Jupiter barycenter',
           '♄': 'Saturn barycenter',
           '⛢': 'Uranus barycenter',
           '♆': 'Neptune barycenter'}

irise = 0
for p in planets:
    print(p)
    # astrometric = earth.at(t0).observe(ephem[planets[p]])
    astrometric = amstercentric.at(t0).observe(ephem[planets[p]])
    ra, dec, distance = astrometric.radec()
    alti, azi, distance = astrometric.apparent().altaz()

    print("  Declinatie: %6.2f Rechte klimming: %6.2f " % (dec.to(units.deg).value, ra.to(units.deg).value))
    if (alti.to(units.deg) > 0.0):
        print ("  Hoogte: %6.2f, azimuth: %6.2f"%(alti.to(units.deg).value, azi.to(units.deg).value))
        ix = radius*(90.0-alti.to(units.deg).value)/90.0*math.sin(-azi.to(units.rad).value)
        iy = radius*(90.0-alti.to(units.deg).value)/90.0*math.cos(-azi.to(units.rad).value)
        d.append(draw.Circle(ix, iy, 1, fill='darkred', stroke_width=1, stroke='darkred'))
        d.append(draw.Text(p, fontsize, ix, iy, center=0.0, fill='black'))
    else:
        f = almanac.risings_and_settings(ephem, ephem[planets[p]], amsterdam)
        t, y = almanac.find_discrete(t0, t1, f)
        for ti, yi in zip(t, y):
            trise = ti.utc_datetime().astimezone(cet).time()
            if yi:
                opkomst = trise.strftime('%H:%M')
                print('  Opkomst om ' + opkomst)
                d.append(draw.Text(p+" "+opkomst, 10, -radius, 1.2*fontsize*irise-radius,
                                   center=0.0, fill='black'))
                irise = irise+1

maanverlicht  = int(100*(almanac.fraction_illuminated(ephem, 'Moon', t0)+0.05))
venusverlicht = int(100*(almanac.fraction_illuminated(ephem, 'Venus', t0)+0.05))
print('Maan '+str(maanverlicht)+'% verlicht')
print('Venus '+str(venusverlicht)+'% verlicht')

d.saveSvg('sterrenhemel.svg')
d.savePng('sterrenhemel.png')
