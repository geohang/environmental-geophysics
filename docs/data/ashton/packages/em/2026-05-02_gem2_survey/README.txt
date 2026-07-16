APLL EM PACKAGE: 2026-05-02 GEM-2 SURVEY

Data class: Real field data
Acquisition date: 2026-05-02
Method: Frequency-domain electromagnetic induction (FDEM)
Instrument: Geophex GEM-2 Ski, hand-held system
Survey organization: Nine survey profiles acquired in one field campaign
Frequencies: 450, 1410, 4350, 13530, and 42150 Hz
Response components: In-phase (I) and quadrature (Q)
Coordinate reference system: NAD83 / UTM zone 15N (EPSG:26915)

CONTENTS
raw/2026-05-02_gem2_raw_averaged_instrument_export.csv
  Original-copy averaged instrument export. This is the earliest retained GEM-2
  table, but it is already averaged and must not be described as unaveraged raw
  time-series data.
processed/2026-05-02_gem2_averaged_inphase_quadrature.csv
  Canonical processed input with the original five-frequency I/Q columns.
location/profile_01_locations.csv through profile_09_locations.csv
  Ordered profile-specific UTM coordinates and elevations. Estimated elevations
  are explicitly identified by the elevation_source field.
metadata/profile_mark_ranges.csv
  Mapping from measurement Mark ranges to Profiles 01-09.
inversion/2026-05-02_gem2_valid_layered_inversion.csv
  Quality-screened layered inversion results. This is a derived product and must
  not be substituted for the I/Q observations in processing workflows.
manifest.json
  Machine-readable package structure, roles, checksums, and acquisition metadata.

USE NOTES
Use metadata/profile_mark_ranges.csv to assign observations to profiles. Join a
profile to its matching location file; do not apply one shared position file to
all profiles. Start processing from the processed I/Q table when reproducing the
PyHydroGeophysX workflow, and use the raw averaged export for lower-level QA.

License: CC BY 4.0. See ../../../DATA_LICENSE.txt.
