# Autorickshaw vs ordinary Indian cars — comparative drag by CFD

**Date:** 2026-08-03 · **Solver:** OpenFOAM v2512, `simpleFoam` (steady RANS, k-ω SST)
**Machines:** Ryzen 5 3600 and Ryzen 5 5600X, 6 MPI ranks each, WSL2 Ubuntu 24.04
(the two reproduce the validation case bit-identically — see §3)

---

## 1. The claim under test

> "An autorickshaw is aerodynamically shit compared to almost any random car."

This report tests the **drag** form of that claim. A second, separate claim was raised
later and is addressed in §7:

> "As a pedestrian on the street, an auto throws more dust in my eyes than a car does."

These need different instruments, and none of the drag results below bear on the dust one.

---

## 2. Result

Mean over the final 200 iterations. `band` is (max−min)/mean across that window.

| vehicle | Cd | band | Aref (m²) | Cd·A | cells | iters |
|---|---|---|---|---|---|---|
| **Autorickshaw** | **0.4337** | 1.0% | 2.162 | **0.938** | 693k | 1000 |
| **Maruti Dzire** | **0.2808** | 4.1% | 2.332 | **0.655** | 561k | 1000 |
| **Maruti WagonR** | **0.3383** | 1.0% | 2.266 | **0.767** | 549k | 1000 |
| **City bus** (upper bound) | **0.5268** | 4.0% | 7.851 | **4.136** | 2.48M | 1000 |

Ratios, autorickshaw against each comparator:

| | vs Dzire | vs WagonR | vs bus |
|---|---|---|---|
| Cd | **1.54×** | **1.28×** | **0.82×** |
| Cd·A (drag force) | **1.43×** | **1.22×** | **0.23×** |
| frontal area | 0.93× | 0.95× | 0.28× |

### What this supports

*An autorickshaw has roughly 1.3× the drag coefficient of a tall boxy hatchback and
1.5× that of a subcompact sedan, at essentially the same frontal area — so it
experiences about 1.2–1.4× the aerodynamic drag force at the same speed.*

Lead with the **WagonR**, not the Dzire. It is the least flattering comparator — tall,
blunt, ubiquitous — and leading with the 1.54× sedan figure reads as comparator-shopping.

### The bus sets the upper bound, and the auto is below it

The bus was run as a **bracket**, not as a peer: it establishes what a genuinely bad road
vehicle shape measures at on this identical pipeline. At **Cd 0.5268** it is 21% worse than
the autorickshaw.

That places the auto in the **middle** of the range, not at the bad end. Ordering by drag
coefficient: bus 0.53 > auto 0.43 > WagonR 0.34 > Dzire 0.28.

On **Cd·A** — the quantity that actually sets fuel burn and, per §7, roughly scales the air
a vehicle throws — the auto is the *second lowest* of the four at 0.938, behind only the two
cars, and **4.4× lower than the bus**. Per passenger carried the gap widens further in the
auto's favour. Any writeup that quotes the Cd ratios without this is cherry-picking.

### What this does NOT support

- **Not "far worse than almost any car."** The margin against a WagonR is 28% on Cd.
  Real, but not dramatic.
- **Not "the worst thing on the road."** A city bus is measurably worse on Cd and vastly
  worse on Cd·A. The auto is unexceptional, not pathological.
- **Not a small-vehicle-with-huge-drag story.** At 2.162 m² the auto's frontal area is
  within 5–7% of both cars. An earlier draft claimed the auto was ~30% smaller frontally;
  that rested on a wrong area measurement and is withdrawn.
- **n = 2 does not support "almost any random car."** A fleet of ordinary Indian vehicles
  (Alto, Swift, i10, Nano, Bolero) is the missing piece. Free model sites skew toward
  supercars, which would bias the comparison in the wrong direction.

### Withdrawn result

An earlier run reported **Cd 0.6083, Aref 1.618, Cd·A 0.984** for the autorickshaw.
**Do not quote those numbers.** They came from corrupted geometry (§5). The corrected run
gives Cd 0.4337 — 29% lower. Two independent signs the new value is the sound one: the
oscillation band tightened from 4.2% to 1.0%, and 0.43 sits within published estimates for
open three-wheelers, whereas 0.61 was high even for that class.

---

## 3. Why these numbers are credible

- The install was validated against OpenFOAM's `motorBike` tutorial, reproducing
  **Cd 0.4159 / Cl 0.0722**, and the same case reproduced **bit-identically on a second
  machine** — the numerics are the reference ones and are machine-independent.
- Every case derives from that validated tutorial. Only geometry, reference area and
  reference length differ. Everything the *comparison* depends on is identical between
  vehicles by construction.
- Both cars landed where published data says they should — subcompact sedan 0.28–0.32,
  tall hatchback ~0.34 — with nothing tuned toward that agreement.
- Comparative RANS is robust where absolute RANS is not: mesh and turbulence-model error
  largely cancel when both bodies run an identical pipeline.

---

## 4. Method

| | |
|---|---|
| freestream | 16.67 m/s (60 km/h) — a speed all these vehicles actually do |
| domain | 42 × 20 × 10 m (cars, auto), 100 × 32 × 14 m (bus) |
| blockage | ~1.2% cars/auto, 1.75% bus |
| base cell | **0.5 m — identical in every case** |
| surface refinement | level 4–5 |
| prism layers | 3 |
| decomposition | 6 MPI ranks |
| iterations | 1000 |

Roughly 5 min meshing + 17 min solving per car; the bus is 2.48M cells and took ~1.4 h.

### Why the bus domain is bigger but the base cell is not

An 11 m vehicle in the 42 m car domain would block ~4% of the cross-section and sit too
close to the outlet, inflating its Cd through confinement rather than shape. **Blockage
ratio, not absolute domain size, is what has to match** between differently sized bodies.

The base cell is deliberately held at 0.5 m across all four cases, because snappyHexMesh
refinement levels are *relative* to it — changing it would silently change the effective
surface resolution and break the comparison the report rests on.

### A rule this project established

**Never quote the last iteration.** Steady RANS on a bluff body does not converge to a
point — it settles into a limit cycle and oscillates indefinitely. An earlier draft quoted
Cd 0.5982 from three adjacent lines of output and called it "converged to four significant
figures"; the true mean was 0.6083 with a 4.2% band. Report the mean over the final 200
iterations, always with the band. More iterations do not help. Only URANS or DES would,
and that needs a cluster.

---

## 5. Geometry, and the failure that had to be caught

All bodies are **voxel-wrapped** — a signed-distance isosurface, manifold by construction,
the same operation commercial surface wrappers perform. This is what makes an arbitrary
downloaded mesh watertight enough for snappyHexMesh.

Vehicles are exported straight out of the Mantaflow comparator blends, so the CFD study
and the earlier 2D slice study provably use the same bodies. Frame throughout: flow +X,
nose at x = 0, ground z = 0, centreline y = 0.

### The autorickshaw wrap destroyed the vehicle, silently

The first auto wrap used a 0.06 m voxel. The autorickshaw's windscreen and canopy roof are
**single-sheet planes with no thickness**, and the wrap erased them. No error, no warning,
and every check in place at the time passed.

They passed because they fired **lateral** rays, which confirmed the open flanks survived —
true, and irrelevant to a missing front face. A **streamwise** census against the raw
source exposed it in one pass:

| height (m) | raw source, first hit x | 0.06 m wrap |
|---|---|---|
| 1.15 | 0.40 / 0.39 / 0.40 | 2.23 |
| 1.30 | 0.48 / 0.47 / 0.48 | none |
| 1.45 | 0.57 / 0.56 / 0.57 | none |

A ray flew 2.23 m into a 2.70 m vehicle. The hole let flow ram into the cabin, which is why
the withdrawn Cd was 29% too high and four times noisier.

The correct geometry already existed: `WRAP_AUTO` in collection `07_WRAP` of
`auto_mantaflow_moving_v2.blend` — a 0.02 m wrap, 80,586 faces, windscreen matching the
source within 1–2 cm at every height.

**The cars and the bus are unaffected.** They are chunky closed bodies with real internal
volume; their streamwise census is textbook, first-hit walking smoothly up bonnet → screen
→ roof with two crossings at every height.

### The bus, by contrast, passed the gate cleanly

Run through the same acceptance test *before* meshing, at 0.02 / 0.03 / 0.06 m. The 0.03 m
wrap was taken. Streamwise first-hit against the raw source:

| height (m) | 0.6 | 1.2 | 1.8 | 2.4 | 2.9 |
|---|---|---|---|---|---|
| raw source | 0.40 | 0.43 | 0.51 | 0.59 | 0.64 |
| 0.03 m wrap | 0.33 | 0.41 | 0.48 | 0.56 | 0.60 |

Every height present in the source is present in the wrap, offset by 3–7 cm in one
consistent direction — the isosurface sitting slightly proud of the surface, which is what
a correct wrap does. Boundary edges 0, non-manifold 0, islands 1. Aref 7.851 m² measured on
a 2 mm raster. Source: 1,780 polys, 10.879 × 2.903 × 3.111 m, already at real-world scale.

**A correction to an earlier draft of this file.** It claimed the 0.06 m bus wrap collapsed
because "solidify thickness must exceed the voxel size." Re-running 0.06 in a clean Blender
session produced 38,152 polys with the correct bounding box, which **disproves that
explanation**. The real cause was `bpy.ops` context reuse across three successive wrap
iterations in one script. The autorickshaw's failure remains explained by thin single-sheet
geometry; the bus never had that defect.

### Geometry acceptance test (now mandatory before any run)

1. Census the **raw source** first — streamwise *and* lateral. That is ground truth.
2. Wrap, then re-run **both** censuses.
3. Pass requires agreement, not plausibility: every height where the source has a face must
   have one in the wrap, offset consistently and by centimetres.
4. `boundary edges = 0`, `non-manifold = 0`, `islands = 1`.
5. Bbox against real-world dimensions — downloaded models arrive at arbitrary scale.

---

## 6. Limitations (these belong in any writeup)

- **No wheel rotation.** Wheels are static geometry. Minor for drag, major for anything
  about dust or spray.
- **No underbody detail.** Voxel wrapping smooths the underbody into a shell.
- **The autorickshaw is simulated EMPTY** — no driver, no passengers. Its most
  aerodynamically flattering configuration.
- **Steady RANS.** Time-averaged flow, no vortex shedding, no unsteady wake.
- **The bus is a Japanese city bus (Nagoya/Aichi), not an Indian one.** No suitable Indian
  bus model was available. It is a generic three-box urban transit shape and is used here
  purely as an upper bound on road-vehicle drag, not as a claim about Indian buses. State
  this wherever the bus number appears.
- **The bus mesh is coarser relative to its size.** 2.48M cells over an 11 m body is a
  lower cells-per-metre density than the cars get. Its Cd carries more uncertainty than the
  others, and its 4.0% band reflects that. It is solid enough to bracket, not to rank
  against the WagonR at a few percent.
- Absolute Cd is approximate. **The ratios are the result.**

---

## 7. The dust and pedestrian question: ANSWERED (transient study, 2026-08-04)

> "I'm a pedestrian on the street. An auto throws more dust in my eyes than a car."

A different claim with a different receptor. Three mechanisms, easily conflated:

| claim | mechanism | status |
|---|---|---|
| the auto *raises* more dust | ground wall shear exceeding the entrainment threshold | indicative only, since wheels do not rotate in these cases |
| *occupants* of the auto eat more dust | open sides, no cabin | 2D slice study, ~40× at chest height |
| the auto throws more air at a *bystander* | wake transport to the kerb at pedestrian height | **answered below** |

### Correction: the wind-tunnel frame is NOT wrong for a pedestrian

An earlier draft of this section asserted that holding the vehicle still puts the
pedestrian "inside a 60 km/h freestream", so only a moving-obstacle Mantaflow setup could
address the claim. **That was wrong.** The lateral component `v_y` is **Galilean
invariant**: shifting to the frame of the pedestrian is the exact transformation
`u_ped = (U_x − U, U_y, U_z)`, not an approximation. A fixed-frame solve therefore answers
a moving-vehicle roadside question exactly, and overset or moving meshes were never
required. The history seen by the pedestrian is read as the diagonal `x = X0 + U·t` through the
`(x, t)` plane data, so no frozen-flow assumption enters either.

Verified with an upstream control: the ground is a slip wall (`U_x = 16.67` exactly at
z = 0), and freestream-subtracted speed upstream of the vehicle reads 0.00–0.07 m/s. Run
that control before believing any subtracted field.

### Method

`pimpleFoam`, transient URANS, k-ω SST, 60 km/h, vertical sampling plane at y = 1.2 m
(the standoff used by the pedestrian), 0 → 2.2 s. Metric is **time-integrated lateral gust energy**
per height band, `E(z) = ∫ ½ρ·v_y² dt` evaluated along the diagonal walked by the
pedestrian. It does not depend on choosing an instant. Two meshes were run: a baseline and a refinement
(`refineFar` box added at x 12–27, `refineWake` extended to x = 30, **`refineNear`
deliberately unchanged** so the near-body face band acts as a control).

### Result: the auto delivers more sideways air at every height, against *both* cars

![Gust energy against height, three vehicles](../report/cfd_f6_heightprofile.png)

*Left: time-integrated lateral gust energy against height. The curve for the auto lies outside
both cars at every height, with a strong bulge at shin level. Right: the ratio, which peaks
near 3.4× low down, dips to about 1.9× at chest, and settles near 2.2× at eye height.*

![Gust energy by band, three vehicles](../report/cfd_f1_height.png)

*The same quantity in the four bands used by earlier drafts, for continuity with numbers
already circulated. Read the profile above for shape, since four fixed heights impose a
ranking that the continuous curves show to be height-dependent.*

| band | auto | WagonR | Dzire | auto/WagonR | auto/Dzire |
|---|---|---|---|---|---|
| ankle 0.20 m | 1.392 | 0.436 | 0.512 | 3.19× | 2.72× |
| knee 0.50 m | 1.801 | 0.557 | 0.682 | 3.23× | 2.64× |
| chest 1.00 m | 0.911 | 0.510 | 0.533 | 1.79× | 1.71× |
| **face 1.60 m** | 0.594 | 0.275 | 0.264 | **2.16×** | **2.25×** |

**The number to quote is 2.2× at face height.** It holds against both cars. Two vehicles differing greatly in shape, and by 20% in steady drag coefficient, land at 2.16× and 2.25×, so the result does not depend on the choice of comparator.

**The ranking of the two cars moves with height, so a best-case and worst-case framing does
not survive.** At ankle level the low sedan scores 0.512 against 0.436 for the tall
hatchback, and above chest the order reverses. A low car drives a strong wake close to the
road and leaves little air disturbed up high. Which car looks worse depends on the height
being asked about, and that is the reason a chart at one fixed height misleads here.

**Mesh status.** Face and chest moved 8–17% between the baseline and the refined mesh, so those are solid. Ankle and knee roughly doubled, which means the low-level magnitudes are still mesh-dependent and only the direction is nailed down. Refining the far wake alone moved the face ratio by 3%, exactly as the control was designed to show. The refinement also revealed that the coarse mesh had been **under**-reading the auto, diffusing away a real ground jet.

**Confound closed (2026-08-05).** `AUTOW_T2R` repeated the auto case on an identical mesh (1 024 831 cells, matched to the cell) with initial turbulent kinetic energy raised 1%. Energies reproduce to **0.0–0.3%** at every band and ratios to 0.3%, so the mesh deltas above belong to the mesh and the pipeline is reproducible end to end. One point of interpretation: URANS is close to deterministic, so treat this as a reproducibility check rather than as an error bar.

### The view from where you stand

![Gust field at the pedestrian](../report/cfd_f4_gustview.png)

*The vehicle drives past a stationary pedestrian standing 1.2 m from the kerb. The frame
change is an exact Galilean shift of the fixed-frame solve, so no re-simulation is involved.
Bright areas are air being thrown by the vehicle, and black is still air.*

Animated versions run the full pass at 9.2× slow motion with three vehicles stacked:
[`cfd_f4_gustview_wide.mp4`](../report/cfd_f4_gustview_wide.mp4) (2640×1484, 16:9) and
[`cfd_f4_gustview_tall.mp4`](../report/cfd_f4_gustview_tall.mp4) (1080×1920, 9:16). At
t = 1.70 s the auto reads **1.03 m/s** of disturbed air at eye height against **0.16 m/s** for
both cars. Note the videos colour by total disturbance `|u - U|`, which is what a person
actually stands in, while the ratios above isolate the sideways component. The
band close to the road appears as one continuous sheet for the auto, while both cars show
separated patches with dark gaps between them.

![Plan view at ankle height](../report/cfd_f5_topview_z0p20.png)

*Seen from above at 0.20 m, coloured by the **sideways** component `|v_y|`, which is the
quantity the headline is built from. Colouring by total disturbance makes the WagonR appear
worst, because the streamwise wake deficit dominates in plan view. That deficit is real and
belongs to the drag discussion in §2.*

> The plan views are the one figure still on the **baseline** mesh and two vehicles. Volume
> writes are needed for a horizontal cut, and only the vertical plane was pulled back for the
> refined runs. Treat them as qualitative. Every number quoted in this section comes from the
> refined mesh. Companion heights:
[1.00 m](../report/cfd_f5_topview_z1p00.png), [1.60 m](../report/cfd_f5_topview_z1p60.png).

### Vertical transport: a difference of degree

| band | auto | WagonR | Dzire |
|---|---|---|---|
| ankle 0.20 m | +0.303 | +0.100 | +0.072 |
| knee 0.50 m | **+0.512** | +0.203 | +0.183 |
| chest 1.00 m | +0.261 | +0.111 | +0.182 |
| face 1.60 m | +0.040 | −0.023 | +0.024 |

Mean signed vertical velocity (m/s, positive means lofting). **All three vehicles loft air at
essentially every height.** The auto lofts 2–3× harder than either car, most strongly at knee
level. Peak sideways air at face height is 2.65 m/s for the auto against 1.81 m/s for the
WagonR.

> **Correction.** An earlier draft of this section reported a sign split, with +0.376 m/s for
> the auto against −0.133 m/s for the WagonR, and argued that the auto lifts air while a car
> presses it down. Measured again per height band across all three vehicles, that result does
> not reproduce, and no band yields −0.133 for the WagonR. The fault was quoting a single
> aggregate over the 0.4–1.6 m column as though it were a per-height figure. The mechanism
> survives as a difference of degree. The opposite-sign claim is **withdrawn**.

### Dust: the passive-scalar argument holds, and no scalar run is needed to state it

Stokes numbers against a ~0.18 s vehicle timescale: 10 µm road dust has settling velocity
0.008 m/s and St ≈ 0.005; 20 µm ≈ 0.02; 50 µm ≈ 0.11. Only near 100 µm (St ≈ 0.45) does a
grain stop following the air. So for PM10 and below, the fraction that hazes air and
reaches eyes, **the air trajectory is the dust trajectory**, and settling is a 2%
correction against the updraught behind the auto. Ballistic grit thrown by tyres remains a separate
Lagrangian problem.

**What is still open:** how high one pass actually carries it. Multiplying the mean
updraught by the wake residence gives ~0.45–0.8 m of rise, so dust entrained at 0–0.5 m
reaches roughly 0.5–1.3 m, which is chest to chin height. That is a crude Lagrangian estimate
from an Eulerian mean and is **not** a result; integrating tracer trajectories through the
time-varying field would settle it.

### Limitations specific to this study

- **n = 3 vehicles** (auto, WagonR, Dzire) brackets the car category at the two ends that
  matter, tall boxy hatchback through low sedan. More vehicles would strengthen the wording
  "almost any random car". Bus geometry is ready at this standard, and Alto, Swift and i10
  are blocked on geometry preparation rather than on compute.
- Ankle and knee ratios are **not grid-converged**. A third, finer mesh is required before
  3.19× can be quoted. Only the direction is established.
- ~~The refined and baseline runs are different realisations~~ **Closed 2026-08-05** by
  `AUTOW_T2R`, the repeat with a perturbed initial condition. Deltas reproduce to 0.0–0.3%,
  see §7. A narrower caveat replaces it: URANS is close to deterministic, so this control
  cannot be read as an uncertainty band on the physics.
- The band tables average over ±0.25 m, so the "ankle 0.20 m" row really covers 0 to 0.45 m
  and overlaps the knee row. That is why the tables put the peak for the auto at knee height
  while the continuous profile puts it at shin height. **Trust the profile for shape.**
  Ratios are unaffected either way.
- Wheels do not rotate, so dust *entrainment* falls outside the model. Only redistribution
  of air is captured.

---

## 8. Visualisation — what the existing data can support

All derivable from fields already on disk (`0`, `500`, `1000` written per case) unless
marked otherwise. **The bus fields live on the second machine** (`atma:~/aero/BUS/`) and
must be pulled before any figure includes it; only its force history has been copied back.

The bus is a strong addition to figures 4 and 7 in particular — at 7.851 m² against the
auto's 2.163 m² it makes the frontal-area and Cd·A panels span a range where the
differences between the three small vehicles stop looking like the whole story.

**Strong, and directly tied to a claim:**

1. **Surface pressure map, all four vehicles, one colour scale.** The auto's flat front panel
   should show a large high-pressure region the Dzire's raked nose does not. This is *the*
   picture of why one Cd is bigger.
2. **Wake volume comparison** — isosurface of total pressure ≈ 0, which encloses the
   separated wake. All three at one scale makes "the auto drags a bigger hole behind it"
   visible rather than asserted.
3. **Cd convergence traces with the ±band shaded**, all vehicles on one axis. Honest about
   the limit-cycle behaviour, and pre-empts the obvious reviewer question.
4. **Frontal-area silhouettes at true relative scale**, annotated with Aref. Kills the
   intuition that the auto is tiny — it isn't, and this report now says so.

**Strong, and specific to the dust claim:**

5. **Streamlines seeded at road level (z = 0.05 m), coloured by final height.** For the
   auto, expect lines entering the open body and exiting sideways at 1–1.7 m; for the car,
   swept over the roof. The single most persuasive image available for the pedestrian claim.
6. **Vertical plane at y = 2.0 m** — the pedestrian's plane — showing turbulent kinetic
   energy, with eye height marked at 1.6 m.

**Cool, and cheap:**

7. **Cd·A drawn as literal rectangles** beside the vehicle silhouettes. Cd·A is the quantity
   that actually sets fuel burn, and it is almost never shown as the area it physically is.
8. **The geometry-failure figure** — broken 0.06 m wrap beside the corrected 0.02 m wrap,
   ray census overlaid. Reviewers trust a study that shows its own caught error.
9. **Q-criterion vorticity iso-surfaces** — spectacular. Caption honestly: with steady RANS
   these are time-averaged structures, not instantaneous vortices.

**Do not attempt from the STEADY (drag) data:**

- Any *animated* wake or shedding sequence. Those solutions are steady; animating one
  would fabricate unsteadiness that was never computed.

**The transient pedestrian cases (§7) lift that restriction — for those cases only.**
They are genuinely time-resolved, so animation shows computed unsteadiness. Delivered:

- `report/cfd_f4_gustview.png` and `.mp4` — side view at the pedestrian's plane, both
  vehicles, full 0–2.2 s pass in the pedestrian's frame.
- `report/cfd_f5_topview_z{0p20,1p00,1p60}.png` — plan view at three heights. A **strip,
  not a film**: the sampler wrote only the vertical plane, so plan views come from volume
  writes stored every 0.5 s. Three instants cannot be interpolated to 30 fps without
  drawing motion the solve never resolved.

Two rules the figure work established, both learned the expensive way:

- **The view must be able to show the finding.** A plan view at one height cannot display
  a result about height; that is what made the first `cfd_f4_planview.png` useless.
- **The plotted quantity must match the claim.** Colouring the plan view by total
  `|u − U∞|` made the WagonR look far worse, because in plan that is dominated by the
  streamwise wake deficit — a *drag* story. Colouring by `|v_y|`, the quantity the ratios
  are built from, agrees with the numbers.

**Note for figure captions:** the existing `paper_figures` set embeds the withdrawn auto
numbers and the caption "Voxel-wrapped 0.06 m envelopes". Both are now wrong — the auto is
0.02 m and its Cd is 0.4337. That set needs regenerating.

---

## 9. Reproducing

```bash
# geometry (Windows, Blender headless)
blender -b --factory-startup --python scratchpad/exportcfd.py

# verify BEFORE running anything
blender -b --factory-startup --python scratchpad/busverify.py

# case + solve (WSL, as user 'foam' -- Open MPI refuses to run as root, and
# every parallel step then silently no-ops while serial steps succeed)
~/bin/mkcase.sh   AUTOW 2.162 2.765
~/bin/runcase.sh  AUTOW

# the bus uses its own case builder (enlarged domain, same 0.5 m base cell)
~/bin/mkcase_bus.sh
~/bin/runcase.sh  BUS

# report -- mean over final 200, never the last line
~/bin/rep.sh AUTOW 2.162
~/bin/rep.sh BUS   7.851
```

Case data: `~/aero/<LABEL>/` in WSL. Geometry: `cfd/geometry/*.stl`.
Vehicle sources: `cfd/vehicles/`.
