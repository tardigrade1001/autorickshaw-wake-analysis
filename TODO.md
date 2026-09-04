# Before public release

Status: the repository regenerates all twelve figures from committed data on a fresh clone.
The items below are what stands between that and a formal reproducible-research release.

## Open

- [ ] **Source the vehicle-class drag ranges.** `analysis/data/tables.py` holds them as
      `PUBLISHED_UNSOURCED` and nothing is plotted from them. A search of reported figures for the
      Dzire clusters nearer 0.32 to 0.33 than the 0.28 to 0.32 quoted in `docs/REPORT.md`
      section 3, so the quoted range needs checking as well as citing. Hucho, *Aerodynamics of
      Road Vehicles* is the standard reference to check first. Restore the band in Figure 2b and
      Figure 4 once a citation exists, and correct section 3 of the report if the range moves.
- [ ] **Verify the animation scripts run from a clean checkout.** `gustdraw.py` is now committed,
      so the imports in `dustvid.py` and `dustcmp.py` resolve. Neither has been executed from
      inside the repository, and both still read field data from absolute `D:` paths.
- [ ] **Test `mkcase.sh` end to end from the repository.** The geometry path is now
      repository-relative and `AUTOW.stl` ships, so an autorickshaw case should build. This has
      not been run since the change.
- [ ] **Decide on the third-party surfaces.** `geometry/README.md` documents how to supply them.
      An open, redistributable comparator car would let a reader reproduce a full comparison.
- [ ] **Configure the git remote and push.** Nothing is pushed yet.

## Done in this pass

- [x] `requirements.txt` with tested Python, NumPy, Matplotlib and imageio-ffmpeg versions
- [x] eight dead `../report/` links in `docs/REPORT.md` repointed to `figures/fields/` and `media/`
- [x] `cfd_f4_gustview_tall.mp4` added, so every report link resolves
- [x] `gustdraw.py` committed, resolving the imports in the two animation scripts
- [x] `geometry/AUTOW.stl` committed with `geometry/README.md` covering provenance, the acceptance
      test and the reference quantities
- [x] `mkcase.sh` reads `geometry/` relative to the repository and fails with a clear message
- [x] shell scripts committed mode 100755
- [x] the machine-independence claim reduced to the two machines tested
- [x] the RANS error-cancellation claim restated as the rationale for reporting ratios
