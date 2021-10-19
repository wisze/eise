# Eise

In the city you do not see the night sky very well. Only the brightest
stars are visible. And because you do not see the whole sky from
between the buildings you have little reference to know what you are
looking at. To know where the planets are in the sky a map would be
handy. Using a raspberry pi, an e-ink display and the impressive
[skyfield pytnon library](https://rhodesmill.org/skyfield/) a small
map is made which updates automatically.

Every fifteen minutes cron starts a short python script which computes
where in the sky the planets are, seen from my Amsterdam location. It
then plots plots the planet symbols on the map of the sky. It computes
the next rise time of the planets which are under the horizon and
lists those planets, with the next rise time, on the left side of the
map. At the bottom of the screen are the cardinal directions in red:
east (o=oost), south (z=zuid) and w for west. On the right side the
time for which the is computed is shown and the illuminated part of
the Moon (☾) and Venus (♀) in percent. For the planet symbols i used
the [Tex cmastro](https://www.ctan.org/tex-archive/fonts/cmastro)
metafont.  I call it **eise** after the builder of [the most beautiful
planetarium in the world](https://www.planetarium-friesland.nl/).

![image of the eise planetmap on an e-ink on a raspberry pi
 zero](https://github.com/wisze/eise/blob/master/1040664.jpg)

[More on my wiki](http://wiki.wisze.org/doku.php/en/ruimte/eise),
[meer op mijn wiki(nl)](http://wiki.wisze.org/doku.php/nl/ruimte/eise)

# Webeise

A similar script draws an svg file with a plot of the stars in the sky
and the locations of the planets. I put the svg on a webserver to make
it available over the net.
