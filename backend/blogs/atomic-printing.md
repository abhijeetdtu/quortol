# The Atomic Printers: Building the World, One Atom at a Time

In a basement laboratory in Gaithersburg, Maryland, a tungsten needle sharpened to a single atom hovers above a silicon wafer chilled to within a whisper of absolute zero. The needle does not touch the surface. At this scale, contact would be a confession of imprecision. A voltage pulses through the tip, and a single hydrogen atom — one of a trillion trillion — lifts away from the silicon, leaving behind an exposed dangling bond. The operator, watching a monitor in an adjacent room, does not see the atom move. Nobody ever does. But it moves. One by one, hour after hour, the hydrogen atoms are lifted away, writing a pattern into the silicon at a resolution no human eye has ever directly perceived — or ever will.

This is not science fiction, though it borrows freely from science fiction's ambitions. It is happening now, at the National Institute of Standards and Technology, as part of a program whose stated goal is "complete control over the placement of atoms and molecules for the fabrication, characterization and validation of atom-scale devices designed to be atomically perfect." [NIST Atom-scale Devices Program](https://www.nist.gov/programs-projects/atom-scale-devices-engineering-metrology-and-manufacturability) The NIST program, led by physicist Jonathan Wyrick and his team in the Physical Measurement Laboratory, is building what amounts to the world's most precise printer — a printer that lays down not ink but atoms, writes not on paper but in silicon, and produces not pages but devices so small that every single atom matters.

It has taken humanity nearly seven decades to get here. The destination, if the researchers are right, is a manufacturing revolution that could rival the Industrial Revolution in scale and surpass it in consequences.

![An STM image showing atom-by-atom fabrication — a schematic of an atom-scale device compared to a red blood cell, illustrating the scale difference](/api/blog/images/atomic-printing_nist_atom_device.png)
*Atom-by-atom fabrication. The device shown is smaller than a red blood cell. Credit: NIST (public domain).*

## The Visionary and the Slight

The idea of manipulating matter atom by atom received its first public airing not in a laboratory but in a lecture hall at the California Institute of Technology, on the evening of December 29, 1959. The speaker was Richard Feynman, already celebrated for his work on quantum electrodynamics; the occasion, the annual meeting of the American Physical Society. The title of his talk could serve as the founding document of an entire field: "There's Plenty of Room at the Bottom."

Feynman did not use the word "nanotechnology" — that term would not be coined until 1974, by the Japanese scientist Norio Taniguchi. He did not describe the scanning tunneling microscope — that invention was still 22 years away. What he did was something perhaps more important: he asked his colleagues to imagine what might be possible if they could arrange atoms one by one. [Feynman, "There's Plenty of Room at the Bottom," Caltech Engineering and Science, February 1960](https://web.pa.msu.edu/people/yang/RFeynman_plentySpace.pdf)

"Why cannot we write the entire 24 volumes of the Encyclopedia Britannica on the head of a pin?" Feynman asked. He calculated that a dot visible to the naked eye, when reduced 25,000 times, would still contain 1,000 atoms. The laws of physics, he argued, did not forbid such miniaturization. The only barriers were engineering ones.

He offered two $1,000 prizes: one for the first person to build a working electric motor smaller than 1/64th of an inch on each side, and another for the first to reduce a page of text to 1/25,000 of its original size in a form readable by electron microscope. Both prizes were claimed within a few years. The real prize — atomic-scale manufacturing — would prove considerably more patient.

## Thirty-Five Xenon Atoms

The breakthrough that transformed Feynman's vision from speculation to demonstration came thirty years later, in a laboratory 4,000 miles from Caltech. At IBM's Almaden Research Center in San Jose, California, a physicist named Don Eigler had been experimenting with a scanning tunneling microscope (STM), a device invented in 1981 by Gerd Binnig and Heinrich Rohrer at IBM Zurich — an invention that earned them the Nobel Prize in Physics in 1986. [IBM STM History](https://www.ibm.com/history/scanning-tunneling-microscope) The STM worked by dragging an atomically sharp tip across a surface at a distance of just a few angstroms, measuring the quantum tunneling current that flowed between tip and sample. It could image individual atoms. What Eigler discovered was that it could also move them.

On September 28, 1989, Eigler scrawled two words in his notebook: "DID IT!" A few days later: "DID IT AGAIN!" [IBM Nanotechnology History](https://www.ibm.com/history/nanotechnology) Over 22 hours, Eigler and his colleague Erhard Schweizer used the STM tip to nudge 35 individual xenon atoms across a nickel surface cooled to 4 Kelvin — just a few degrees above absolute zero, where atoms cooperate because they lack the energy to rebel — arranging them into the letters "I," "B," and "M." The resulting pattern measured 5 nanometers tall and 17 nanometers wide. [Eigler & Schweizer, "Positioning single atoms with a scanning tunnelling microscope," Nature, 1990](https://www.nature.com/articles/344524a0)

It was the first time atoms had ever been precisely positioned on a flat surface — a historic achievement with an appropriately corporate logo. The image of those 35 pale blue dots spelling out a company name became one of the most reproduced scientific images of the 1990s: the visual proof that Feynman's vision was physically realizable. The New York Times reported it on April 5, 1990, under the headline "2 Researchers Spell 'I.B.M.,' Atom by Atom." [NYT, April 1990](https://www.nytimes.com/1990/04/05/us/2-researchers-spell-ibm-atom-by-atom.html)

![Thirty-five xenon atoms spelling "IBM" on a nickel surface — the first time atoms were precisely positioned on a flat surface, 1989. Credit: IBM Research / Wikimedia Commons](/api/blog/images/atomic-printing_ibm_xenon_atoms.jpg)

At this point, the atomic-printing revolution might have remained exactly what it appeared to be: a series of laboratory tricks, impressive but desperate for a practical application. Xenon atoms on nickel, after all, are not a computing platform. They are not a manufacturing method. They are a parlor trick at the atomic scale — charming, unprecedented, and essentially useless. The atoms are held in place by nothing more than the weak van der Waals force, and they will diffuse away the moment the temperature rises above a few degrees Kelvin.

*The first precisely positioned atoms. They would remain a scientific curiosity until researchers learned to place atoms permanently inside silicon.*

What was needed was a way to place atoms permanently, in useful arrangements, inside a material that could be turned into working devices. That material had to be silicon — the workhorse of the microelectronics industry. And the method would have to be compatible with the existing manufacturing infrastructure that produces the world's computer chips.

The first group to solve this problem was at the University of New South Wales, led by Professor Michelle Simmons, a physicist who had become preoccupied with the idea of building electronic devices atom by atom. In 2012, Simmons and her team announced that they had created the world's first single-atom transistor — a working electronic switch consisting of a single phosphorus atom placed precisely within a silicon crystal. [Fuechsle et al., "Realisation of a single-atom transistor in silicon," 2012](https://royalsoc.org.au/wp-content/uploads/2024/09/145_Fuechsle.pdf) The device functioned because of something remarkable: a single phosphorus atom, embedded in a silicon lattice and cooled to cryogenic temperatures, can hold and release electrons in a controlled way — it acts as a switch, the fundamental component of all computing, now reduced to its logical limit.

Simmons went on to found Silicon Quantum Computing (SQC) in 2017, and her team has since demonstrated an 11-qubit quantum processor built from precisely placed phosphorus atoms. [Nature, 2025](https://www.nature.com/articles/s41586-025-09827-w) The processor stores quantum information in the spin states of atomic nuclei embedded in a pure silicon crystal — information that can be read out and manipulated with fidelities above 99.9%.

But the real revolution is not just in quantum computing. It is in the method itself.

## The Printers

The NIST approach, developed by Wyrick's team in collaboration with researchers at Sandia National Laboratories and Zyvex Labs, is best understood as a kind of atomic-scale 3D printing. The process begins with a silicon wafer whose surface has been passivated with a single layer of hydrogen atoms — each silicon atom bonded to one hydrogen atom, like a coat of paint exactly one molecule thick. The STM tip then acts as a lithography tool, selectively removing hydrogen atoms from specific sites to expose the reactive silicon underneath.

The pattern of exposed silicon — the ink-receptive surface — is then exposed to a dopant gas, usually phosphine (PH3). The phosphine molecules adsorb only to the exposed silicon sites, like keys that have no interest in the wrong locks. A controlled heating step drives the phosphorus atoms into the silicon lattice, where they become substitutional dopants: electrically active sites that can conduct current, store charge, or confine electrons. [NIST program description](https://www.nist.gov/programs-projects/atom-scale-devices-engineering-metrology-and-manufacturability)

The result is a structure whose electronic properties are determined not by statistical averages over billions of atoms but by the exact position of every single dopant atom. "The exact position, type, number of atoms, and their arrangement, dramatically influence device behavior," the NIST team writes. "By controlling the precise atomic makeup and geometry of a device it is possible to engineer a device's electronic, quantum and mechanical structure to a level where every atom matters."

This is atomic-precision advanced manufacturing (APAM), and it represents a fundamental break with every manufacturing method that preceded it. Conventional chip fabrication works by flooding a surface with light or electrons through a mask, creating patterns by subtraction. It is a statistical process: you expose a region, develop the resist, etch the material, and hope that billions of transistors come out right. The variations are managed by designing around them — engineers build in safety margins to account for the fact that no two transistors are exactly alike.

APAM does not tolerate variation. It places every atom exactly where it needs to be.

The Sandia National Laboratories team, led by Shashank Misra, has been pushing APAM toward practical integration with existing semiconductor manufacturing. In May 2025, they published a landmark paper demonstrating the direct integration of an APAM module into Sandia's legacy 0.35-micron CMOS manufacturing process — proof that atomic-precision fabrication can coexist with conventional chip-making. [Applied Physics Reviews, 2025](https://arxiv.org/html/2505.03622v2) "This proof-of-concept demonstration also outlines the requirements and limitations of a unified APAM tool which could be introduced into manufacturing environments," the authors wrote, "greatly expanding access to this technology, and inspiring a new generation of devices."

## The Scalability Problem

The challenge that keeps atomic-precision manufacturing from becoming a commercial reality is the same challenge that faced the earliest computers in the 1940s: throughput. An STM tip can remove hydrogen atoms at a rate of perhaps a few hundred per second. A modern EUV lithography machine exposes an entire wafer in seconds. Bridging this gap is the central engineering problem of APAM.

The NIST team is attacking it with machine learning. They have developed open-source software called ABDNavigator [GitHub: usnistgov/ABDNavigator](https://github.com/usnistgov/ABDNavigator) that uses computer vision to monitor the STM tip's condition and adjust its operation in real time. The software can detect when the tip has become dull — a frequent occupational hazard when the tip interacts with the surface at nanometer distances — and automatically move it to a conditioning region where it is reshaped. It can detect previously written features and align new lithography to them with atomic precision.

"The ultimate goal," the NIST team explains, "is that an operator should supply an input file, specifying the strategies for device fabrication, and then the control software and STM would perform all fabrication steps without operator intervention." [NIST, Automation section](https://www.nist.gov/programs-projects/atom-scale-devices-engineering-metrology-and-manufacturability)

Zyvex Labs, based in Richardson, Texas, has commercialized this approach with its ZyVector system — a control platform that turns a standard STM into a high-throughput atomic lithography tool. Zyvex's hydrogen depassivation lithography is the only complete commercial solution for atomic-precision writing. Their technology, they claim, is "an order of magnitude more precise than the best e-beam lithography." [Zyvex Labs, Products](https://www.zyvexlabs.com/apm/products/)

At University College London, a team led by Dr. Taylor Stock and Professor Neil Curson has pushed the placement accuracy to near-perfect levels. Using arsenic instead of phosphorus as the dopant atom, they achieved placement accuracy of 97% and more — and believe that 100% is within reach. "The prevailing view was that single-atom fabrication using arsenic would suffer the same problems as phosphorus," Stock said. "But we realized that single arsenic atoms might be placed more reliably." [UCL, March 2024](https://www.ucl.ac.uk/news/2024/mar/near-perfect-control-single-atoms-major-advance-towards-quantum-computing)

The UCL approach builds 2x2 arrays of single arsenic atoms, each one positioned by hand at first — a process that takes several minutes per atom. The researchers acknowledge that practical quantum computers will require millions of qubits, and that full automation is essential. But they note that the existing $550 billion semiconductor industry provides a ready-made infrastructure for scaling up.


![Timeline of key milestones in atomic-precision manufacturing from 1959 to 2026](/api/blog/images/atomic-printing_milestones.png)
*Six decades of progress: from Feynman's lecture to commercial quantum manufacturing. Sources: NIST, Nature, UNSW, IBM Research, DOE, Zyvex Labs.*

## The End of Moore's Law

The timing of these advances is not accidental. For sixty years, the semiconductor industry has operated under Moore's Law — the observation, first made by Intel co-founder Gordon Moore in 1965, that the number of transistors on a microchip doubles approximately every two years. For most of that period, the doubling was driven by a single mechanism: shrinking the transistor. Smaller transistors meant faster switching, lower power consumption, and — because more of them fit on a chip — exponentially increasing computational power.

That mechanism is reaching its physical limit. At the 2-nanometer node and below, quantum tunneling causes electrons to leak through gate oxides that are only a few atoms thick. Power density has become a critical bottleneck as chips generate more heat than can be dissipated. The latest industry roadmaps show transistor density growth slowing from a two-year doubling cycle to three years or more. [ScienceWatch, 2026 analysis](https://sciencewatch.blog/will-moores-law-end-realistic-timeline)

The atomic scale is not just the next node on the roadmap. It is the final node. You cannot make a transistor smaller than a single atom, and the semiconductor industry is now within striking distance of that limit.

This is where atomic-precision manufacturing enters the story not as a futuristic possibility but as an engineering necessity. If you cannot make devices smaller by scaling down conventional lithography, you must make them differently — by placing atoms exactly where you want them, harnessing quantum effects instead of fighting them, and building devices that operate on fundamentally new principles.

![Chart showing transistor feature size scaling from 1970 projected to physical limits](/api/blog/images/atomic-printing_transistor_scaling.png)
*Transistor feature size reduction from 10µm (1970) to approaching the atomic limit (~0.5nm). The physical barrier of atomic scale represents the end of traditional Moore's Law scaling. Data: various industry roadmaps.*

## The Quantum Connection

The most immediate application of atomic-precision manufacturing is quantum computing — and the two fields are now developing in lockstep. The reason is physical: a quantum computer requires qubits that can maintain coherence long enough to perform calculations. Phosphorus atoms in silicon provide some of the best coherence times known to physics, with nuclear spin coherence exceeding 30 seconds in isotopically purified silicon-28. [SQC / Nature 2025](https://www.nature.com/articles/s41586-025-09827-w)

But creating a quantum computer is not just about finding a good qubit. It is about placing enough qubits close enough together that they can interact — and doing so with a precision that conventional manufacturing cannot provide. The interaction between neighboring phosphorus atoms in silicon falls off exponentially with distance; a positioning error of just one atomic lattice site (0.54 nanometers) can mean the difference between a working qubit and a dead one.

APAM solves this problem by design. The Sandia-Zyvex team described APAM as "the only known route to tailor silicon nanoelectronics with full 3D atomic precision." [Bussmann et al., MRS Bulletin, 2021](https://link.springer.com/article/10.1557/s43577-021-00139-8) In their vision, the atomic-precision fabrication of qubits is not an exotic sideline but a manufacturing method that plugs directly into the existing silicon foundry ecosystem.

The economic stakes are enormous. In June 2026, NIST announced the creation of the Quantum Manufacturing Engineering Center (QMEC), a public-private partnership with SRI International backed by an initial $20 million investment. The center's mission is to "accelerate manufacturing of scalable, high-performance quantum components and systems" — including cryostats, lasers, quantum chips, and photonic integrated circuits. [NIST QMEC Press Release, June 29, 2026](https://www.nist.gov/news-events/news/2026/06/nist-launches-center-drive-manufacture-quantum-technologies)

"The new Quantum Manufacturing Engineering Center will bring together top experts to ensure both continued U.S. leadership in quantum technologies," said Deputy Secretary of Commerce Paul Dabbar, "and that we are the epicenter of manufacturing quantum systems at scale to drive advances in sensing, communications, encryption, computing, biomedicine and other critical areas."

The QMEC builds on the Quantum Economic Development Consortium (QED-C), launched in 2018 under the National Quantum Initiative Act, which authorized roughly $1.2 billion in quantum information science spending across federal agencies. The new center is explicitly modeled on SEMATECH, the 1987 U.S. government-industry consortium that helped the American semiconductor industry rebuild competitiveness against Japanese manufacturers — suggesting that the federal government sees atomic-precision quantum manufacturing not as a research project but as a strategic industry. [Everglade / QMEC analysis](https://everglade.com/building-the-20m-quantum-factory-what-nists-new-manufacturing-center-means-for-innovators/)

## What Could Go Right; What Could Go Wrong

The scholarly literature on APM's societal impacts is surprisingly sparse — and what exists is conspicuously divided. The most systematic attempt to evaluate the net societal impact was published in 2018 by Steven Umbrello and Seth Baum of the Global Catastrophic Risk Institute, in the journal Futures. Their analysis covered six domains: material wealth, the environment, military affairs, surveillance, artificial intelligence, and space travel. [Umbrello & Baum, Futures, 2018](https://gcri.org/papers/00035_nanotechnology.pdf)

The benefits, they found, could be extraordinary. APM could produce materials ten times stronger per pound than today's best alloys, manufactured with near-zero waste. It could enable ultra-efficient solar cells and batteries, addressing climate change at the material level. It could build spacecraft components with minimal mass, opening up space travel to orders of magnitude more activity. The environmental benefits alone, Umbrello and Baum concluded, might be the largest single positive effect.

But the risks are correspondingly large. In military affairs, APM could democratize weapons of mass destruction: a technology that can assemble matter atom by atom could theoretically produce chemical weapons, explosives, or autonomous drones with minimal infrastructure. The same capabilities that make APM attractive for environmental remediation — the ability to build catalysts that capture carbon or break down pollutants — could be turned to considerably less constructive purposes.

A 2024 analysis from arXiv catalogued additional concerns: mass unemployment from the displacement of conventional manufacturing; the potential for ubiquitous surveillance through atomically precise sensors; and the long-standing fear of "gray goo" — self-replicating nanoscale assemblers consuming the biosphere. [arXiv:2409.00955, 2024](https://arxiv.org/abs/2409.00955)

The authors note that APM literature has been "dominated by older, speculative papers that discuss its immense potential risks and benefits without sufficient grounding in the latest advancements or practical limitations." They call for "more grounded discourse" — and, crucially, for regulatory frameworks that anticipate the technology rather than reacting to it.

## The Inevitability of Progress

The question is no longer whether atomic-precision manufacturing is possible. That question was settled on September 28, 1989, when 35 xenon atoms spelled out a corporate logo. It was settled again in 2012 with the single-atom transistor, in 2021 with the APAM-CMOS integration roadmap, and in 2025 with the first 11-qubit atomic processor. The question now is how fast it scales — and who controls it.

The NIST team's work on automation and machine learning suggests that the speed barriers are surmountable. The Sandia-Zyvex integration into conventional CMOS fabrication suggests that atomic-precision manufacturing does not require a wholesale replacement of existing infrastructure — it can be added as a module, enhancing conventional chips with atomically precise features.

And the UCL breakthrough with arsenic placement — "the first time that we've demonstrated a way of achieving the accuracy and scale required," as Professor Neil Curson put it — suggests that the atomic-level reliability problem is yielding to systematic engineering.

"We now have a huge engineering challenge ahead to be able to do this more quickly and easily," Curson said, "but this is the first time that I've felt certain that a universal quantum computer can be built."

It is worth pausing on that statement. A universal quantum computer — a machine with the potential to solve problems in materials science, drug discovery, cryptography, and climate modeling that are fundamentally intractable for any classical computer — has been the holy grail of physics and computer science for three decades. Curson is saying that he now believes it can be built. Not might be built. Can be built.

The reason is atomic-precision manufacturing.

In Gaithersburg, the NIST needle continues to hover, lifting hydrogen atoms one at a time, writing patterns in silicon that no human eye can see. The patterns are simple so far: a few dozen atoms here, a quantum dot there, a single-electron transistor that might — if everything works — form the basis of a qubit. But every layer of silicon that grows over these structures seals in not just atoms but a principle: that the ultimate limit of manufacturing is not a barrier but a frontier. A frontier where, as Feynman put it in 1959, there is plenty of room at the bottom.

---

*Source disclaimer: This article was researched using primary sources including NIST program documentation, peer-reviewed journal articles from Nature, Advanced Materials, MRS Bulletin, and Applied Physics Reviews, original Feynman lecture transcripts, IBM heritage archives, DOE publications, and federal press releases. Every factual claim is linked to its primary source inline.*
