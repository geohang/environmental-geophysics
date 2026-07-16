APLL SRT PACKAGE: 2026-05-02 LINE 2000

Data class: Real field data
Acquisition date: 2026-05-02
Method: Seismic refraction tomography (SRT)
Receiver setup: 24 geophones at nominal 2 m spacing
Source: Sledgehammer impact on an aluminum plate
Acquisition: Three impacts were collected at each source station for stacking
and noise reduction. Source stations extend 4 m beyond both ends of the receiver
spread. The supplied geometry contains 28 positions at 2 m spacing (0 to 54 m).

CONTENTS
data/line_2000.sgy
  Raw SEG-Y waveform data for this line.
location/line_2000_positions_utm.txt
  Ordered source/receiver geometry in UTM coordinates with elevations.
location/line_2000_positions_wgs84.csv
  The same 28 positions with UTM and WGS84 coordinates.
processed/line_2000_first_break_picks.csv
  Interpreted first-arrival picks with trace and geometry metadata.

USE NOTES
The first-break table is interpreted data, not raw acquisition. Keep it separate
from the SEG-Y waveforms when testing picking or uncertainty workflows.

License: CC BY 4.0. See ../../../DATA_LICENSE.txt.
