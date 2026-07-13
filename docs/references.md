# References and Further Reading

The course text is Reynolds (2011). The books and papers below extend it: general method references, the electrical and hydrogeophysical literature that several modules draw on, and the open-source software used in the notebooks. Every entry has a DOI or ISBN so you can find it directly. A BibTeX block for all entries is at the bottom of the page.

## Course Textbook

- Reynolds, J. M. (2011). *An Introduction to Applied and Environmental Geophysics* (2nd ed.). Wiley-Blackwell. ISBN 978-0-471-48536-0.

## General Applied and Environmental Geophysics

- Telford, W. M., Geldart, L. P., & Sheriff, R. E. (1990). *Applied Geophysics* (2nd ed.). Cambridge University Press. ISBN 978-0-521-33938-4.
- Kearey, P., Brooks, M., & Hill, I. (2002). *An Introduction to Geophysical Exploration* (3rd ed.). Blackwell Science. ISBN 978-0-632-04929-5.
- Everett, M. E. (2013). *Near-Surface Applied Geophysics*. Cambridge University Press. ISBN 978-1-107-01877-8.

## Electrical Methods and Petrophysics

- Archie, G. E. (1942). The electrical resistivity log as an aid in determining some reservoir characteristics. *Transactions of the AIME*, 146(1), 54-62. [doi:10.2118/942054-G](https://doi.org/10.2118/942054-G)
- Loke, M. H., Chambers, J. E., Rucker, D. F., Kuras, O., & Wilkinson, P. B. (2013). Recent developments in the direct-current geoelectrical imaging method. *Journal of Applied Geophysics*, 95, 135-156. [doi:10.1016/j.jappgeo.2013.02.017](https://doi.org/10.1016/j.jappgeo.2013.02.017)
- Binley, A., & Slater, L. (2020). *Resistivity and Induced Polarization: Theory and Applications to the Near-Surface Earth*. Cambridge University Press. ISBN 978-1-108-49274-4.

## Hydrogeophysics and the Critical Zone

These references connect the geophysical methods to subsurface hydrology, the theme of the course notebooks and of Dr. Chen's research group.

- Rubin, Y., & Hubbard, S. S. (Eds.). (2005). *Hydrogeophysics*. Springer (Water Science and Technology Library, Vol. 50). ISBN 978-1-4020-3101-4.
- Binley, A., Hubbard, S. S., Huisman, J. A., Revil, A., Robinson, D. A., Singha, K., & Slater, L. D. (2015). The emergence of hydrogeophysics for improved understanding of subsurface processes over multiple scales. *Water Resources Research*, 51(6), 3837-3866. [doi:10.1002/2015WR017016](https://doi.org/10.1002/2015WR017016)
- Parsekian, A. D., Singha, K., Minsley, B. J., Holbrook, W. S., & Slater, L. (2015). Multiscale geophysical imaging of the critical zone. *Reviews of Geophysics*, 53(1), 1-26. [doi:10.1002/2014RG000465](https://doi.org/10.1002/2014RG000465)

## Software and Computational Tools

The course notebooks use these open-source libraries. PyHydroGeophysX is developed in Dr. Chen's group and ties the hydrological and geophysical sides of the course together.

- Chen, H., Niu, Q., & Wu, Y. (2026). PyHydroGeophysX: An extensible open-source platform for integrating hydrological models with geophysical measurements. *SoftwareX* (in press). Software archive: [doi:10.5281/zenodo.17025139](https://doi.org/10.5281/zenodo.17025139). Code: [github.com/geohang/PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX).
- Rücker, C., Günther, T., & Wagner, F. M. (2017). pyGIMLi: An open-source library for modelling and inversion in geophysics. *Computers & Geosciences*, 109, 106-123. [doi:10.1016/j.cageo.2017.07.011](https://doi.org/10.1016/j.cageo.2017.07.011)

## BibTeX

Copy any entry into your `.bib` file.

```bibtex
@book{reynolds2011,
  author    = {Reynolds, John M.},
  title     = {An Introduction to Applied and Environmental Geophysics},
  edition   = {2nd},
  publisher = {Wiley-Blackwell},
  year      = {2011}
}

@book{telford1990,
  author    = {Telford, W. M. and Geldart, L. P. and Sheriff, R. E.},
  title     = {Applied Geophysics},
  edition   = {2nd},
  publisher = {Cambridge University Press},
  year      = {1990}
}

@book{kearey2002,
  author    = {Kearey, Philip and Brooks, Michael and Hill, Ian},
  title     = {An Introduction to Geophysical Exploration},
  edition   = {3rd},
  publisher = {Blackwell Science},
  year      = {2002}
}

@book{everett2013,
  author    = {Everett, Mark E.},
  title     = {Near-Surface Applied Geophysics},
  publisher = {Cambridge University Press},
  year      = {2013}
}

@article{archie1942,
  author  = {Archie, Gustave E.},
  title   = {The electrical resistivity log as an aid in determining some reservoir characteristics},
  journal = {Transactions of the AIME},
  volume  = {146},
  number  = {1},
  pages   = {54--62},
  year    = {1942},
  doi     = {10.2118/942054-G}
}

@article{loke2013,
  author  = {Loke, M. H. and Chambers, J. E. and Rucker, D. F. and Kuras, O. and Wilkinson, P. B.},
  title   = {Recent developments in the direct-current geoelectrical imaging method},
  journal = {Journal of Applied Geophysics},
  volume  = {95},
  pages   = {135--156},
  year    = {2013},
  doi     = {10.1016/j.jappgeo.2013.02.017}
}

@book{binley2020,
  author    = {Binley, Andrew and Slater, Lee},
  title     = {Resistivity and Induced Polarization: Theory and Applications to the Near-Surface Earth},
  publisher = {Cambridge University Press},
  year      = {2020}
}

@book{rubin2005,
  editor    = {Rubin, Yoram and Hubbard, Susan S.},
  title     = {Hydrogeophysics},
  publisher = {Springer},
  series    = {Water Science and Technology Library},
  volume    = {50},
  year      = {2005}
}

@article{binley2015,
  author  = {Binley, Andrew and Hubbard, Susan S. and Huisman, Johan A. and Revil, Andre and Robinson, David A. and Singha, Kamini and Slater, Lee D.},
  title   = {The emergence of hydrogeophysics for improved understanding of subsurface processes over multiple scales},
  journal = {Water Resources Research},
  volume  = {51},
  number  = {6},
  pages   = {3837--3866},
  year    = {2015},
  doi     = {10.1002/2015WR017016}
}

@article{parsekian2015,
  author  = {Parsekian, A. D. and Singha, K. and Minsley, B. J. and Holbrook, W. S. and Slater, L.},
  title   = {Multiscale geophysical imaging of the critical zone},
  journal = {Reviews of Geophysics},
  volume  = {53},
  number  = {1},
  pages   = {1--26},
  year    = {2015},
  doi     = {10.1002/2014RG000465}
}

@article{ruecker2017,
  author  = {R{\"u}cker, Carsten and G{\"u}nther, Thomas and Wagner, Florian M.},
  title   = {pyGIMLi: An open-source library for modelling and inversion in geophysics},
  journal = {Computers \& Geosciences},
  volume  = {109},
  pages   = {106--123},
  year    = {2017},
  doi     = {10.1016/j.cageo.2017.07.011}
}

@software{chen2026_pyhydrogeophysx,
  author    = {Chen, Hang},
  title     = {PyHydroGeophysX: Integrating Hydrological Models with Geophysical Measurements},
  version   = {0.3.0},
  year      = {2026},
  doi       = {10.5281/zenodo.17025139},
  url       = {https://github.com/geohang/PyHydroGeophysX}
}

@article{chen2026_softwarex,
  author  = {Chen, Hang and Niu, Qifei and Wu, Yuxin},
  title   = {PyHydroGeophysX: An Extensible Open-Source Platform for Integrating Hydrological Models with Geophysical Measurements},
  journal = {SoftwareX},
  year    = {2026},
  note    = {In press}
}
```
