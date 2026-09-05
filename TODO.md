# Before public release

Status: the repository regenerates all twelve figures from committed data on a fresh clone,
rebuilds an OpenFOAM case from the committed geometry, and runs both animation scripts end to end.

## Open

Empty. Both release items are closed, listed below.

## Closed in this pass (2026-09-05)

- [x] **Published (2026-09-05).** Live at
      https://github.com/tardigrade1001/autorickshaw-wake-analysis, public, branch `main`,
      with the description and topics set.
- [x] **Vehicle-class drag ranges resolved by removing them.** Every figure
      reachable online for these classes traces back to a secondary compilation, so a range
      here would look like a reference and rest on hearsay. `PUBLISHED_UNSOURCED` is gone from
      `analysis/data/tables.py`, the dead band-drawing code is gone from `fig_drag.py` and
      `fig_method.py`, and Figure 4 has lost a legend swatch that advertised bands the figure
      never drew. Section 3 of the README and the report now name the DrivAer body
      (Heft, Indinger and Adams, SAE Technical Paper 2012-01-0168) as the standard open
      geometry for a car-shaped verification case, which is the sound way to get a measured
      comparison.
## Done in this pass (2026-09-05)

- [x] The bus model traced: Japanese bus "Nagoya City Bus" (Aichi) by VRC-IW, **CC
      Attribution-NonCommercial**. `BUS.stl` stays out, because a NonCommercial derivative
      cannot be released under the repository's CC BY 4.0. The bus contributes measured
      numbers and no geometry to any figure, so nothing depends on shipping it.
- [x] Geometry licences traced through the Sketchfab API. The autorickshaw, WagonR and
      Dzire source models are all Creative Commons Attribution, so their wraps ship here
      with credit to Nirmal.Justin and BHP3D. `geometry/`, `LICENSE` and section 11 of the
      README record author, model link and licence for each.
- [x] `WAGONR.stl` and `DZIRE.stl` committed, MD5-matched to the surfaces the reported runs
      used. The three-vehicle comparison now reproduces from the repository alone.
- [x] Corrected the provenance claim. The autorickshaw was recorded as modelled for this
      study. It is a wrapped derivative of a third-party model, like both cars.

- [x] `analysis/paths.py` resolves every field, output and geometry location through
      `VEHICLE_AERO_FIELDS`, `VEHICLE_AERO_OUT` and `VEHICLE_AERO_GEOMETRY`, each with the
      local default recorded. A missing input now names the path it wanted and the variable
      that changes it. `python analysis/paths.py` prints the whole resolution table.
- [x] `dustplane.py`, `dustvid.py` and `dustcmp.py` read through it. The silhouettes come from
      the repository's own `geometry/AUTOW.stl`.
- [x] Both animation scripts run from inside the repository, in both layouts. A third
      argument caps the snapshot count for a seconds-long smoke test, writing beside the
      master file, leaving the finished animation in place.
- [x] Regression check on the refactor: `extract_diagonal.py` regenerates
      `data/diagonal_profiles.npz` byte for byte, and the waist ratio reads
      auto 0.4280 / WagonR 0.0184 = 23.2, matching the published number.
- [x] `mkcase.sh` verified end to end from the repository. Built under a throwaway label,
      meshed and solved: **906,995 cells**, the same single skewness warning, matching the
      original `AUTOW` case exactly.
- [x] `docs/REPORT.md` brought onto the house prose rules. 35 em dashes, 12 semicolons and
      every contrastive construction removed, with the meaning unchanged. The one remaining
      "while" sits inside a verbatim quote of a withdrawn claim and stays.
- [x] The two uncited agreement claims in section 2 and section 3 now say in the report
      itself that the quoted ranges carry no citation.

## Done earlier

- [x] `requirements.txt` with tested Python, NumPy, Matplotlib and imageio-ffmpeg versions
- [x] eight dead `../report/` links in `docs/REPORT.md` repointed to `figures/fields/` and `media/`
- [x] `cfd_f4_gustview_tall.mp4` added, so every report link resolves
- [x] `gustdraw.py` committed, resolving the imports in the two animation scripts
- [x] `geometry/AUTOW.stl` committed with `geometry/README.md` covering provenance, the
      acceptance test and the reference quantities
- [x] `mkcase.sh` reads `geometry/` relative to the repository and fails with a clear message
- [x] shell scripts committed mode 100755
- [x] the machine-independence claim reduced to the two machines tested
- [x] the RANS error-cancellation claim restated as the rationale for reporting ratios
