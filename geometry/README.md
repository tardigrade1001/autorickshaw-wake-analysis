# Vehicle surfaces

`mkcase.sh` reads `geometry/<LABEL>.stl`. Override the directory with `STL_OVERRIDE` when the
surfaces are staged elsewhere.

| file | status | source |
|---|---|---|
| `AUTOW.stl` | included | autorickshaw, modelled and voxel-wrapped for this study at 0.02 m |
| `WAGONR.stl` | obtained separately | third-party model, voxel-wrapped at 0.02 m |
| `DZIRE.stl` | obtained separately | third-party model, voxel-wrapped at 0.02 m |
| `BUS.stl` | obtained separately | third-party model of a Nagoya city bus, voxel-wrapped at 0.03 m |

The three third-party surfaces stay outside this repository because they are derived works of
models this study did not author. Any closed vehicle surface at real-world scale substitutes for
them, and the pipeline is agnostic to the source.

## Preparing a surface

Voxel-wrap the source mesh as a signed-distance isosurface, then run the acceptance test in
section 7 of `../README.md` before meshing. The test requires:

- a streamwise and a lateral ray census against the raw source
- every height where the source has a face also present in the wrap, offset consistently and by
  centimetres
- `boundary edges = 0`, `non-manifold = 0`, `islands = 1`
- a bounding box checked against real-world dimensions

A 0.06 m wrap erased the autorickshaw windscreen and inflated its Cd by 29%, which is the failure
this test exists to catch. Figure 12 shows the census that exposed it.

Frame convention throughout: flow along +X, nose at x = 0, ground at z = 0, centreline at y = 0.

## Reference quantities

`mkcase.sh` takes the frontal area and the moment reference length as arguments. The values used
in this study:

| vehicle | A_ref (m2) | CofR x (m) |
|---|---|---|
| autorickshaw | 2.162 | 2.765 |
| WagonR | 2.266 | 3.585 |
| Dzire | 2.332 | 3.995 |
| bus | 7.851 | 10.879 |

Frontal areas were measured on a 2 mm raster of the wrapped surface.
