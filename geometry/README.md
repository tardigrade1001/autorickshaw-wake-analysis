# Vehicle surfaces

`mkcase.sh` reads `geometry/<LABEL>.stl`. Override the directory with `STL_OVERRIDE` when the
surfaces are staged elsewhere.

| file | status | source model | author | licence |
|---|---|---|---|---|
| `AUTOW.stl` | included | [Low Poly Autorickshaw aka TukTuk](https://sketchfab.com/3d-models/low-poly-autorickshaw-aka-tuktuk-c7c87455ad014b3f9fc8c9fb2d164a61) | Nirmal.Justin | CC Attribution |
| `WAGONR.stl` | included | [2013 Suzuki WagonR](https://sketchfab.com/3d-models/2013-suzuki-wagonr-71112627f42342099ff95b59e7532663) | BHP3D | CC Attribution |
| `DZIRE.stl` | included | [2022 Maruti Suzuki Swift Dzire](https://sketchfab.com/3d-models/2022-maruti-suzuki-swift-dzire-95451c00cb2d48778f67d798167e7237) | BHP3D | CC Attribution |
| `BUS.stl` | obtained separately | [Japanese bus "Nagoya City Bus" (Aichi)](https://sketchfab.com/3d-models/japanese-bus-nagoya-city-bus-aichi-37c0a04a7aef4139b6aa037d17e768e5) | VRC-IW | CC Attribution-NonCommercial |

Each included file is a voxel-wrapped derivative of the model beside it, made for this study. The
autorickshaw and both cars are wrapped at 0.02 m, the bus at 0.03 m. Every licence above was read
from the Sketchfab API on 2026-09-05, and the derivatives are redistributed here under the same
terms with attribution to the original authors.

The bus surface stays outside the repository. The source model is CC Attribution-NonCommercial,
and CC BY 4.0 covers the rest of this material, so a NonCommercial derivative needs separate
terms. Shipping it would carry a non-commercial restriction into an otherwise permissive
repository. The bus contributes measured numbers to the report, and every figure here builds from
the three included surfaces. Any closed vehicle surface at real-world scale substitutes for it,
and the pipeline is agnostic to the source.

The three included files are byte-identical to the surfaces the reported runs used, checked by MD5
against `constant/triSurface/vehicle.stl` in each solved case.

## Preparing a surface

Voxel-wrap the source mesh as a signed-distance isosurface, then run the acceptance test in
section 7 of `../README.md` before meshing. The test requires:

- a streamwise and a lateral ray census against the raw source
- every height where the source has a face also present in the wrap, offset consistently and by
  centimetres
- `boundary edges = 0`, `non-manifold = 0`, `islands = 1`
- a bounding box checked against real-world dimensions

A 0.06 m wrap erased the autorickshaw windscreen and inflated the Cd by 29%, which is the failure
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
