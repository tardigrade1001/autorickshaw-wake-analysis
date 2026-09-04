"""Values quoted in the report, committed so every figure number is traceable.

Each table records the section of docs/REPORT.md it comes from. Values computed
directly from field data are NOT duplicated here: those figures read the data.
"""

# --- drag, REPORT.md section 2. Mean over the final 200 iterations. -------------
# band is (max - min) / mean across that window.
DRAG = {
    #  key        Cd      band    Aref     CdA     cells
    "auto":   dict(cd=0.4337, band=0.010, aref=2.162, cda=0.938, cells=693_000),
    "wagonr": dict(cd=0.3383, band=0.010, aref=2.266, cda=0.767, cells=549_000),
    "dzire":  dict(cd=0.2808, band=0.041, aref=2.332, cda=0.655, cells=561_000),
    "bus":    dict(cd=0.5268, band=0.040, aref=7.851, cda=4.136, cells=2_480_000),
}

# Withdrawn autorickshaw result, from the corrupted 0.06 m wrap. REPORT.md s2.
WITHDRAWN_AUTO = dict(cd=0.6083, band=0.042, aref=1.618, cda=0.984)

# Indicative class ranges quoted in REPORT.md s3. NO PRIMARY SOURCE has been
# traced for these values, and a search of reported figures for the Dzire
# clusters nearer 0.32-0.33 than the 0.28-0.32 quoted there. They are retained
# here for the record and are NOT plotted or used as a validation check until a
# citable source is attached. See TODO.md.
PUBLISHED_UNSOURCED = {"dzire": (0.28, 0.32), "wagonr": (0.32, 0.36)}
PUBLISHED = {}          # empty: nothing is drawn from an uncited range

# Validation against the OpenFOAM motorBike tutorial, reproduced bit-identically
# on two machines. REPORT.md s3.
VALIDATION = dict(cd=0.4159, cl=0.0722)

# --- pedestrian gust energy, REPORT.md section 7 -------------------------------
# Time-integrated lateral gust energy along the pedestrian diagonal, refined mesh.
GUST = {
    #  height_m   auto    wagonr   dzire
    0.20: (1.392, 0.436, 0.512),
    0.50: (1.801, 0.557, 0.682),
    1.00: (0.911, 0.510, 0.533),
    1.60: (0.594, 0.275, 0.264),
}

# Mean signed vertical velocity, m/s, positive means lofting. REPORT.md s7.
VERTICAL = {
    0.20: (+0.303, +0.100, +0.072),
    0.50: (+0.512, +0.203, +0.183),
    1.00: (+0.261, +0.111, +0.182),
    1.60: (+0.040, -0.023, +0.024),
}

# --- geometry acceptance test, REPORT.md section 5 -----------------------------
# Streamwise first-hit distance (m) into the autorickshaw. None means no hit.
# The 0.06 m wrap erased the windscreen and canopy roof.
RAY_CENSUS = {
    #  height_m: (raw source, 0.06 m wrap)
    1.15: (0.40, 2.23),
    1.30: (0.48, None),
    1.45: (0.57, None),
}
VEHICLE_LENGTH = 2.70

# Bus wrap, which passed the same gate cleanly. REPORT.md s5.
BUS_CENSUS = {0.6: (0.40, 0.33), 1.2: (0.43, 0.41),
              1.8: (0.51, 0.48), 2.4: (0.59, 0.56), 2.9: (0.64, 0.60)}

# --- source-height experiment, measured from field data ------------------------
# Reported here only as the derived summary. The figure reads the fields.
SOURCE_HEIGHT = dict(lift=0.5, ceiling_gain=0.2, eye_fraction=0.028, eye_level=1.66)
