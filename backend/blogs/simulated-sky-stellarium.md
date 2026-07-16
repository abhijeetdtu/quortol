# From Stone Circles to Software: The Simulated Sky

She sits in a dim room in Vienna, a laptop glow the only light. On the screen, the sky over Salisbury Plain fades from blue to violet to black. The date is December 21, 2500 BCE. The sun sinks toward a notch in the landscape she knows will align with the Heel Stone at Stonehenge. She presses a key; the simulation slows to real-time. The sun touches the horizon exactly where the archaeologists predicted.

Twenty years ago, a researcher attempting this would have needed a mainframe, a grant, and a team of programmers — or a box of paper star charts, a calculator, and long nights of trigonometric drudgery. Today, she uses Stellarium: a free, open-source planetarium that began in 2001 as a French developer's hobby project and has since become the quiet workhorse of an unexpected field — cultural astronomy.

![Stonehenge at sunset, painted by John Constable in 1836 — the same monument, the same sun, not yet the software to simulate what they meant.](/api/blog/images/simulated-sky-stellarium_stonehenge.jpg)

---

It is easy to forget, in an age of GPS satellites and weather apps, that for most of human history the sky was the only calendar, the only clock, the only navigation system. Every culture looked up and imposed meaning on the lights above. The Pleiades rising at dawn marked the start of the agricultural season for the Māori; the passage of the Milky Way told the Boorong people of southeastern Australia when to hunt for emu eggs; the slow wobble of Earth's axis — precession — erased and replaced the pole star every few millennia, forcing each civilization to begin again its reckoning with the architecture of the heavens.

Stellarium, launched by Fabien Chéreau in 2001 and now stewarded by a global community of developers including Alexander Wolf, Georg Zotti, and Guillaume Chéreau, bridges this ancient need and modern technology in ways its creators never intended. What began as a pretty sky simulator — something to make your desktop look interesting — has become what archaeoastronomer Clive Ruggles calls "the foremost tool for archaeoastronomical visualisations" [https://web.cliveruggles.com/index.php/tools](https://web.cliveruggles.com/index.php/tools). The peer-reviewed paper by Zotti et al. (2021), published in the *Journal of Skyscape Archaeology*, formalizes what the community had long understood: Stellarium had become indispensable for understanding how our ancestors saw the stars [https://doi.org/10.1558/jsa.17822](https://doi.org/10.1558/jsa.17822).

## Before the Digital Sky

Before there was software, there was hardware — and it was of astonishing ingenuity.

The oldest surviving star map in the Anglo-American tradition is Simeon de Witt's "Astrolabe for Latitude 41," drawn in 1780 — a brass-and-paper analog computer that could tell time, find stars, and predict sunrise with nothing but moving parts and careful engraving [Astrolabe for Latitude 41 — Smithsonian National Museum of American History](https://americanhistory.si.edu/collections/object/nmah_997048). Earlier still, the Soochow Planisphere of 1247 CE — a Chinese star chart carved in stone — maps 1,565 stars across 283 asterisms with a precision that still impresses astronomers today [Soochow Planisphere — Picryl](https://picryl.com/media/soochow-planisphere-a52483). Johannes Hevelius, in 1690, published *Firmamentum Sobiescianum* with elaborate engraved constellation figures — the swans and bears and heroes of classical Western astronomy rendered in baroque detail [Johannes Hevelius constellation engraving — public domain].

![Simeon de Witt's 'Astrolabe for Latitude 41' (1780) — a hand-drawn paper planisphere that served as star map, clock, and perpetual calendar. Smithsonian National Museum of American History (CC0).](/api/blog/images/simulated-sky-stellarium_dewitt_astrolabe.jpg)

![The Soochow Planisphere (1247 CE) — a star chart engraved in stone during the Song Dynasty, mapping 1,565 stars across 283 asterisms. Public domain.](/api/blog/images/simulated-sky-stellarium_soochow_planisphere.jpg)

![Orion from Johann Bayer's Uranometria (1603) — the classical Western constellation that guided the eye of European astronomers for centuries. Public domain.](/api/blog/images/simulated-sky-stellarium_uranometria_orion.jpg)

These were the tools of the trade for centuries: paper planispheres, astrolabes, celestial globes, numerical tables. They worked. But they were static. You could not ask an astrolabe to show you what the sky looked like from Giza on the summer solstice of 4500 years ago — and if you could, it would have no answer to give.

The 20th century changed that. The optomechanical planetarium — most famously the Zeiss projectors — created immersive indoor skies, projecting thousands of stars onto a dome while gears and motors simulated planetary motion, precession, and even the slow shift of the equinoxes. For the first time, one could sit inside a machine and watch the sky bend. But these instruments were enormous and enormously expensive. Zotti et al. note that "high construction and running costs meant that they have not become common" [https://doi.org/10.1558/jsa.17822](https://doi.org/10.1558/jsa.17822). A Zeiss projector cost millions; a dedicated building for it cost millions more. Archaeoastronomy — already a niche discipline perched between archaeology and astronomy — could rarely secure either.

![A Zeiss planetarium projector, the 20th-century's answer to the simulated sky — immersive but enormously expensive. Credit: Mike Peel / Science Museum London (CC-BY-SA 4.0).](/api/blog/images/simulated-sky-stellarium_zeiss_projector.jpg)

## The Accidental Planetarium

Fabien Chéreau was a software developer with a side project. In 2001, he started writing a program that would render a realistic 3D night sky on a home computer. It used OpenGL, a graphics library more commonly associated with video games. He called it Stellarium — a Latin-tinged word meaning "place of stars."

The appeal was immediate and viral. Stellarium was free. It was beautiful. You could set your location anywhere on Earth and see exactly which stars were overhead. By 2006, the project won a SourceForge Project of the Month award and took gold at Les Trophées du Libre, the French open-source software competition. Developers began contributing: Alexander Wolf took over maintenance and core development; Georg Zotti, a researcher at VRVis in Vienna, began pushing the software toward rigorous scientific accuracy; Guillaume Chéreau, Fabien's brother, contributed to the rendering engine [https://www.vrvis.at/en-us/about-us/team/infos/zotti-georg](https://www.vrvis.at/en-us/about-us/team/infos/zotti-georg). The project grew the way open-source constellations do: by attraction, not by design.

Stellarium now catalogs over 600,000 stars and 80,000 deep-sky objects. It simulates the solar system with high precision. It accounts for atmospheric refraction, light pollution, and the fading afterglow of twilight. And, crucially, it can travel through time — which turns out to be the feature that matters most.

## Sky Cultures: The Constellations of Everyone

Western astronomy inherited its constellations from the Greeks via the Arabs and the Renaissance. Orion, Ursa Major, Cassiopeia — these are the shapes most of the world learns in school. But they are far from universal.

The Māori saw the Milky Way as a canoe with a long wake. The Inuit of the Arctic recognized a constellation called *Qilugtussat* — the dogs — circling the celestial pole. The Kamilaroi people of New South Wales looked at the Southern Cross and saw a wedge-tailed eagle. The Babylonians, writing on clay tablets in the second millennium BCE, grouped stars into the three "paths" of Anu, Enlil, and Ea — the earliest known constellation system. There are, it turns out, as many skies as there are people to look up.

In 2014, sky culture researcher Susanne M. Hoffmann began working with the Stellarium team to add non-Western constellation systems to the software. The project now includes more than forty sky cultures from around the world [https://github.com/Stellarium/stellarium-skycultures](https://github.com/Stellarium/stellarium-skycultures). Babylonian (MUL.APIN), Chinese (both traditional and contemporary), Māori, Inuit, Aztec, Norse, Navajo, Boorong, Polynesian — each is rendered as a complete system of asterisms and star names, drawn from ethnographic and historical records. The SkyCultureMaker plugin allows anyone with expertise in an underrepresented tradition to create and contribute a new sky culture.

This is not merely an academic exercise. For indigenous communities working to revitalize traditional knowledge, Stellarium offers a way to see the sky as their ancestors did — to recover a cultural landscape that colonialism and urbanization erased. For researchers, it opens a comparative astronomy that was impossible with analog tools.

## The Time Machine

Taking Stellarium back in time requires more than simply turning the clock backward.

Earth's rotation is slowing, very gradually, due to tidal friction from the Moon. The difference is small — milliseconds per century — but it accumulates. Without correcting for this, a simulation of the sky over Stonehenge in 2500 BCE would be off by hours. Stellarium implements the ΔT (Delta T) correction, a set of historical and astronomical models that account for the known deceleration.

Precession — the slow 26,000-year wobble of Earth's axis — shifts the positions of the equinoxes and the identity of the pole star. The star Thuban was the pole star when the Great Pyramid of Giza was built; today Polaris holds that title; in 13,000 years, Vega will. Stellarium simulates precession, nutation (smaller wobbles superimposed on precession), and the full orbital mechanics of the solar system. Since version 0.15, the software can use NASA/JPL DE430 and DE431 ephemerides — the same high-precision datasets that guide spacecraft — to compute planetary positions from 13,000 BCE to 17,000 CE [https://github.com/Stellarium/stellarium/wiki/Research](https://github.com/Stellarium/stellarium/wiki/Research).

The ArchaeoLines plugin, developed by Georg Zotti, overlays the vertical lines of declination, solstice and equinox sunrise/sunset directions, and horizon altitude profiles that are the bread and butter of archaeoastronomical fieldwork [https://doi.org/10.1007/978-3-319-97007-3_12](https://doi.org/10.1007/978-3-319-97007-3_12). Where a field archaeologist might spend weeks taking measurements with a theodolite, a Stellarium user can replicate the observations in minutes — and test hypotheses about alignments that no living person has ever seen.

## Walking into the Past

The landscape matters. A solstice sunrise is only meaningful relative to the horizon it rises over — which is to say, a solstice sunrise is only as good as the ground it touches.

The Scenery3D plugin extends Stellarium beyond the sky, allowing users to embed three-dimensional reconstructions of ancient structures within their landscapes, under the skies of their era. In 2016 and 2017, this was put to spectacular use at the MAMUZ Museum in Mistelbach, Austria, where a Stonehenge exhibition used Stellarium-powered projections to show visitors what the monument looked like — and what sky it sat under — when it was first built [https://publications.archpro.science/publication/zotti-2019-b/](https://publications.archpro.science/publication/zotti-2019-b/). Museumgoers could watch the sun rise over the Heel Stone 4,500 years ago without leaving the gallery.

Researchers have used the same tools for serious fieldwork. The Roman archaeoastronomy of Hadrian's Villa has been studied with Stellarium simulations. Giulio Magli, a leading figure in the field, used Stellarium to investigate the orientations of Angkor Wat's temples in Cambodia. A paper by Zotti and colleagues on "Virtual Archaeoastronomy" demonstrates the workflow end to end: survey a site, model it in 3D, place it in the Stellarium sky, and test alignment hypotheses against the software's high-precision ephemerides [https://doi.org/10.1007/978-3-319-97007-3_12](https://doi.org/10.1007/978-3-319-97007-3_12).

## The Open-Source Advantage

Commercial planetarium software exists. Some of it is very good. But for cultural astronomy research, Stellarium has become dominant for reasons that have nothing to do with marketing budgets.

It is free. A graduate student in Nigeria, a curator in Delhi, a hobbyist in rural Montana — all can download it and run it on modest hardware. It is customizable. If your research requires a correction factor not in the default simulation, you can modify the source code. It is extensible. The plugin architecture means that anyone with programming skills can add new functionality. It is scriptable, allowing researchers to automate complex sequences of simulations and produce reproducible results — essential for scientific publication. And the sky cultures, maintained on a separate open-source repository, grow richer with every contribution [https://github.com/Stellarium/stellarium](https://github.com/Stellarium/stellarium).

The software reached version 1.0 in October 2022 — more than two decades after its first commit [https://stellarium.org/release/2022/10/01/stellarium-1.0.html](https://stellarium.org/release/2022/10/01/stellarium-1.0.html). The latest version as of mid-2026 is 26.2 [https://stellarium.org/](https://stellarium.org/). It includes more than thirty-five calendrical systems, including the Gregorian, Julian, Egyptian, Babylonian, French Revolutionary, and Maya Long Count — because if you are simulating the sky of another culture, you should be able to see it through their calendar as well.

Clive Ruggles, Emeritus Professor of Archaeoastronomy at the University of Leicester and perhaps the most respected figure in the field, maintains a page on his website surveying digital tools for archaeoastronomy. Stellarium is the only software he describes as "the foremost tool." That endorsement carries the weight of someone who spent decades doing this work with slide rules and theodolites — and who knows, better than most, what it means to have found something better.

## The Sky, Open to All

There is a quiet wonder in this. Stellarium is, at its core, a tool of empathy. It lets you step into another vantage point — another century, another latitude, another system of belief — and see the same stars arranged differently.

You can stand on the Giza plateau in 2560 BCE and watch the belt of Orion set behind the Pyramid of Menkaure. You can toggle the sky culture to Babylonian and trace MUL.APIN on a night when Sargon of Akkad might have seen it. You can switch to the Boorong sky culture, and recognize the emu in the Milky Way as the same dark rift that a Kamilaroi elder calls *Warrumbul*.

The paper by Zotti, Hoffmann, Wolf, Chéreau, and Chéreau — five authors spanning research institutes and open-source communities — documents what Stellarium has become [https://arxiv.org/abs/2104.01019](https://arxiv.org/abs/2104.01019). But it cannot capture what Stellarium *does*, which is simpler and stranger: it gives anyone with a computer the ability to look up at the sky and see it through another culture's eyes. That is not merely a technical achievement. It is a human one — and the human ones are always harder.

The researcher in Vienna closes her laptop. The simulation ends. But the sky outside — the real sky, with its real stars — is the same sky that shone over every culture that ever was. Stellarium, in the end, is merely a way of learning to see it.

[Stellarium](https://stellarium.org/) is free and open-source software. The sky cultures repository is at [github.com/Stellarium/stellarium-skycultures](https://github.com/Stellarium/stellarium-skycultures). The full research paper is available at [https://doi.org/10.1558/jsa.17822](https://doi.org/10.1558/jsa.17822) and on [arXiv](https://arxiv.org/abs/2104.01019).
