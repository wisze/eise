from skyfield import almanac
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos, mpc
from astropy import units
from datetime import datetime
from pytz import timezone
import numpy as np
import math

ts = load.timescale()
ephem = load('de421.bsp')
cet = timezone('CET')

sun, moon, earth = ephem['sun'], ephem['moon'], ephem['earth']

amsterdam = Topos('52.3679 N', '4.8984 E')
amstercentric = earth + amsterdam

t0 = ts.now()
t1 = ts.tt_jd(t0.tt + 1)
nu = t0.utc_datetime().astimezone(cet).time().strftime('%H:%M')

mindist=1.5
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
with load.open(mpc.COMET_URL,reload=True) as f:
    comets = mpc.load_comets_dataframe(f)
print('Found ',len(comets), ' comets')
comets = (comets.sort_values('reference')
          .groupby('designation', as_index=False).last()
          .set_index('designation', drop=False))
f = open('cometlist.txt', 'w')
for (c, cometdata) in comets.iterrows():
    comet = sun + mpc.comet_orbit(cometdata, ts, GM_SUN)
    ra, dec, distance = sun.at(t0).observe(comet).radec()
    print(c,' is at ',distance.au,'au')
    if (distance.au < mindist):
       f.write(c+"\n")
f.close()
