# Before public release

Status: the repository regenerates all twelve figures from committed data on a fresh clone,
rebuilds an OpenFOAM case from its own geometry, and runs both animation scripts end to end.

## Open

- [ ] **Source the vehicle-class drag ranges.** `analysis/data/tables.py` holds them as
      `PUBLISHED_UNSOURCED` and nothing is plotted from them. A web search reaches only
      secondary compilations, so this needs the book: Hucho, *Aerodynamics of Road Vehicles*.
      Restore the band in Figure 2b and Figure 4 once a citation exists. Section 3 of
      `docs/REPORT.md` now states plainly that the ranges carry no citation, so the report is
      accurate as it stands and the citation upgrades it.
- [ ] **Decide on the third-party surfaces.** `geometry/README.md` documents how to supply
      them. An open, redistributable comparator car would let a reader reproduce a full
      comparison.
- [ ] **Configure the git remote and push.** Nothing is pushed yet. Needs a repository name
      and a public or private decision.

## Done in this pass (2026-09-05)

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
