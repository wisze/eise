from skyfield.api import load
from skyfield.elementslib import osculating_elements_of
from skyfield.data.spice import inertial_frames

ecliptic = inertial_frames['ECLIPJ2000']

ts = load.timescale()
t = ts.utc(2000, 1, 1)
t = ts.now()

eph   = load('de421.bsp')
earth = eph['earth']
sun   = eph['sun']

planeten = {'Maan': 'Moon', 'Mercurius': 'Mercury', 'Venus': 'Venus',
           'Zon': 'Sun', 'Mars': 'Mars',
           'Jupiter': 'Jupiter barycenter', 'Saturnus': 'Saturn barycenter'}

f = open('orbits.csv', 'w')
print('naam,a,b,e,T,lon_node,l_peri,omega_peri,t_peri',file=f)

for p in planeten:
    if (p == 'Zon' or p == 'Maan'):
        position = (eph[planeten[p]] - earth).at(t)
    else:
        position = (eph[planeten[p]] - sun).at(t)
    
    elements = osculating_elements_of(position, ecliptic)

    # The elements are then attributes of the Elements object:
    i = elements.inclination.degrees
    e = elements.eccentricity
    a = elements.semi_major_axis.km
    b = elements.semi_minor_axis.km
    T = elements.period_in_days
    O = elements.longitude_of_ascending_node

    print(p)
    print('   Inclination:  {0:.2f} degrees'.format(i))
    print('   Eccentricity: {0:.5f}'.format(e))
    print('   Semimajor axis: {0:.0f} km'.format(a))
    print('   Semiminor axis: {0:.0f} km'.format(b))
    print('   Longitude of ascending node {0:.2f}', format(O))

    pt = elements.periapsis_time
    pl = elements.longitude_of_periapsis
    po = elements.argument_of_periapsis

    print('   Periapsis:', pt.utc_strftime())
    print('   Period: {0:.2f} days'.format(T))
    print('   Longitude of periapsis {0:.2f}', format(pl))
    print('   Argument of periapsis ', po)

    print(p,',',a,',',b,',',e,',',T,',',O.degrees,',',pl.degrees,',',po.degrees,',',pt.tdb,file=f)
    
    next = pt + elements.period_in_days
    print('   Next periapsis:', next.utc_strftime())
