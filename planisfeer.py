from skyfield import almanac
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos, mpc
from astropy import units
from datetime import datetime
from pytz import timezone
import drawsvg as draw
import numpy as np
import math

# maxalt = 60.0
magnitude = 4.0
mindist=1.0
radius = 500
margin=50
cometfont=8
textfont=12
planetfont=12
d = draw.Drawing(2*radius+margin, 2*radius+margin, origin='center', displayInline=False)
# Draw the horizon circle
d.append(draw.Circle(0, 0, radius, fill='lightgrey', stroke_width=2, stroke='black'))

ts = load.timescale()
ephem = load('https://raw.githubusercontent.com/skyfielders/python-skyfield/master/ci/de421.bsp')
cet = timezone('CET')

sun, moon, earth = ephem['sun'], ephem['moon'], ephem['earth']

amsterdam = Topos('52.3679 N', '4.8984 E')
amstercentric = earth + amsterdam

t0 = ts.now()
t1 = ts.tt_jd(t0.tt + 1)
nu = t0.utc_datetime().astimezone(cet).time().strftime('%H:%M')

# Teken helderste sterren in
istars=0
print("Teken sterrenkaart")
with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)
df = df[df['magnitude'] <= magnitude]
bright_stars = Star.from_dataframe(df)
astrometric = amstercentric.at(t0).observe(bright_stars)
alt, az, distance = astrometric.apparent().altaz()
for alti, azi, mag in zip(alt.degrees, az.degrees, df['magnitude']):
    if (alti > 0.0):
        ix = radius*(90.0-alti)/90.0*math.sin(np.deg2rad(-azi))
        iy = radius*(alti-90.0)/90.0*math.cos(np.deg2rad(-azi))
        d.append(draw.Circle(ix, iy, magnitude-mag,
            fill='white', stroke_width=0.8, stroke='black'))
        istars = istars+1
print(istars,"sterren boven de horizon")

# Comets!
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
with load.open(mpc.COMET_URL) as f:
    comets = mpc.load_comets_dataframe(f)
print(len(comets), "kometen gevonden")
comets = (comets.sort_values('reference')
          .groupby('designation', as_index=False).last()
          .set_index('designation', drop=False))
f = open("cometlist.txt",'r')
for name in f:
    row = comets.loc[name.strip()]
    comet = sun + mpc.comet_orbit(row, ts, GM_SUN)
    ra, dec, distance = sun.at(t0).observe(comet).radec()
    print(name.strip(),"at",distance.au,"AU")
    if (distance.au < mindist):
       astrometric = amstercentric.at(t0).observe(comet)
       alti, azi, distance = astrometric.apparent().altaz()
       if (alti.to(units.deg) > 0.0):
           print (name.strip(),"hoogte: %6.2f, azimuth: %6.2f"%(alti.to(units.deg).value, azi.to(units.deg).value))
           ix = radius*(90.0-alti.to(units.deg).value)/90.0*math.sin(-azi.to(units.rad).value)
           iy = radius*(alti.to(units.deg).value-90.0)/90.0*math.cos(-azi.to(units.rad).value)
           d.append(draw.Circle(ix, iy, 1, fill='darkred', stroke_width=1, stroke='blue'))
           d.append(draw.Text(name.strip(), cometfont, ix, iy, center=0.0, fill='grey'))

# Teken planeten in
planets = {'☉': 'Sun', '☾': 'Moon', '☿': 'Mercury', '♀': 'Venus', '♂': 'Mars',
           '♃': 'Jupiter barycenter', '♄': 'Saturn barycenter',
           '⛢': 'Uranus barycenter',  '♆': 'Neptune barycenter'}

irise = 0
for p in planets:
    astrometric = amstercentric.at(t0).observe(ephem[planets[p]])
    alti, azi, distance = astrometric.apparent().altaz()
    if (alti.to(units.deg) > 0.0):
        print (p,"hoogte: %6.2f, azimuth: %6.2f"%(alti.to(units.deg).value, azi.to(units.deg).value))
        ix = radius*(90.0-alti.to(units.deg).value)/90.0*math.sin(-azi.to(units.rad).value)
        iy = radius*(alti.to(units.deg).value-90.0)/90.0*math.cos(-azi.to(units.rad).value)
        d.append(draw.Circle(ix, iy, 1, fill='darkred', stroke_width=1, stroke='darkred'))
        d.append(draw.Text(p, planetfont, ix, iy, center=0.0, fill='black'))
    else:
        f = almanac.risings_and_settings(ephem, ephem[planets[p]], amsterdam)
        t, y = almanac.find_discrete(t0, t1, f)
        for ti, yi in zip(t, y):
            trise = ti.utc_datetime().astimezone(cet).time()
            if yi:
                opkomst = trise.strftime('%H:%M')
                print(p,"opkomst om",opkomst)
                d.append(draw.Text(p+" "+opkomst, textfont, -radius, 1.2*textfont*irise-radius,
                                   center=0.0, fill='black'))
                irise = irise+1

maanverlicht  = int(100*(almanac.fraction_illuminated(ephem, 'Moon', t0)+0.05))
venusverlicht = int(100*(almanac.fraction_illuminated(ephem, 'Venus', t0)+0.05))
print('Maan',str(maanverlicht)+'% verlicht')
print('Venus',str(venusverlicht)+'% verlicht')

d.save_svg('planisfeer.svg')
# d.save_png('planisfeer.png') # planeetsymbolen komen niet door in png plot
