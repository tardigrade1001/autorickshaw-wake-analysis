# Case inventory

Each directory holds `0.orig`, `constant` and `system` for one OpenFOAM case. Meshes,
`processor*` directories and `postProcessing` output are excluded, because they run to gigabytes
and regenerate from these dictionaries.

Superseded and discontinued runs are retained where the reason for discontinuing them explains the
adopted method. They are named with a suffix and are listed separately below.

## Steady cases, used for the drag result

| case | vehicle | reported in |
|---|---|---|
| `AUTO` | autorickshaw, first wrap | superseded, see below |
| `AUTOW` equivalent | autorickshaw, 0.02 m wrap | Figure 4, Cd 0.434 |
| `WAGONR` | Maruti WagonR | Figure 4, Cd 0.338 |
| `DZIRE` | Maruti Dzire | Figure 4, Cd 0.281 |
| `BUS` | Japanese city bus | Figure 4, Cd 0.527 |

## Transient cases, used for the exposure and dust results

| case | purpose |
|---|---|
| `AUTOW_T`, `WAGONR_T` | baseline mesh, first gust-energy pass |
| `AUTOW_T2`, `WAGONR_T2`, `DZIRE_T2` | refined mesh, the source of every quoted gust ratio |
| `AUTOW_T2R` | reproducibility control, cell-matched mesh with initial k raised 1% |
| `AUTOW_F` | first dust attempt, diffusive wall source |
| `AUTOW_D` | dust source as an advected inlet layer, the configuration that worked |
| `WAGONR_D` | the same dust supply on the WagonR, the comparison in Figure 8 |
| `AUTOW_R` | dust source lifted to 0.5 to 1.0 m, the experiment in Figure 11 |

`AUTOW_F` produced a null tracer, so its velocity field carries the result and its scalar field
does not. The fix in `AUTOW_D` supplies dust as a layer carried in by the flow.

The `AUTOW_D` inlet profile specifies a layer from 0 to 0.28 m. Upstream of the vehicle the mesh
is at the 0.5 m base cell, and `fixedProfile` evaluates at face centres, so the layer actually
supplied spans 0 to 0.5 m. `AUTOW_R` is therefore the same 0.5 m slab lifted by exactly 0.5 m,
which makes the pair a single-variable comparison. The nominal dictionary values alone would
suggest otherwise.

## Retained superseded runs

| directory | what it records |
|---|---|
| `AUTOW_T2R.bad_012000`, `AUTOW_T2R.bad_182909` | earlier attempts at the reproducibility control |
| `DZIRE_T2.failed_np12_172513` | a 12-rank decomposition on a 6-core machine |

The Dzire failure is the origin of the one-rank-per-physical-core rule used in every later run.
Open MPI also refuses to run as root, and `--allow-run-as-root` silently produces a case that was
never decomposed, so every run here executes as an unprivileged user.
