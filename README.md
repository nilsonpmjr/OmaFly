# OmaFly (Experimental Version)

<p align="center">
  <img src="assets/fly.svg" width="128" alt="OmaFly">
</p>

An experimental desktop pet fly for Omarchy/Hyprland, featuring 2D pixel art and behavioral decisions driven by a neural network incorporating circuits from FlyWire. The implementation prioritizes low power consumption; the small circuit runs on a compiled native CPU core, with a validated comparative proof on the GPU.

## Current Status
The project is currently in the feasibility prototype phase (V0.2).
- **What's working:** An escape and exploration prototype (with a functional neural network), a visual interface in PySide6/QML, a system tray icon control, and an optimized C++ core (low CPU impact). Neural shelter selection, physical entry, occlusion, and return are integrated; 27 automated tests and a real-window neural probe pass.
- **What's missing:** The full catalog of 10 behavioral responses, broader shelter calibration and desktop validation, and automatic installation/packaging as a native plugin for Omarchy.

The overlay now uses Qt Quick's software renderer by default. In the latest short comparison, total proportional memory fell from about 181 MiB to 126 MiB, with about 1.4% of one CPU core. Both renderers measured roughly 6 W for the whole GPU while active; the earlier 17–18 W observation was not reproduced, so its cause remains unconfirmed. See [renderer measurements and limits](reports/RENDER-POWER.md).

## Future Vision
The plan for the release version (M3/V1.0) involves testing and integrating all 10 responses simultaneously. Post-V1, there are planned expansions (P2) that include new responses to visual threats and virtual CO2, precise traceability with the database (BANC/FlyWire), and an improved system for neural persistence between startups.

## Data Requirements
Due to their large size, the connectome data files are not included in this repository. Before building, you must download the FlyWire FAFB v783 dataset files and place them in the root directory:
- `fafb-consolidated_cell_types.csv.gz`
- `fafb-classification.csv.gz`
- `fafb-neurons.csv.gz`
- `fafb-connections_princeton.csv.gz`

*(Note: The large `fafb-sk_lod1_783_healed.zip` file containing 3D skeletons is only used for offline anatomical analysis and is not required to run the desktop pet).*

## Preparation and Execution
To prepare and run from checkout:

```sh
python tools/build.py
python tools/build_assets.py
python tools/extract.py
./run.sh run
```

The command opens only the tray icon; turn on the fly via the menu or with `./run.sh enable`. `./run.sh disable` suspends the simulation and removes the overlay; `./run.sh quit` terminates the instance. See [execution, tests, and limits](docs/IMPLEMENTATION.md).

| Document | Usage |
|---|---|
| [PRD](docs/PRD.md) | Experience, requirements, ten behavioral responses, and product priorities. |
| [Technical Spec](docs/SPEC.md) | Proposed architecture, contracts, and feasibility proofs; `/to-spec` delivery. |
| [TODO and Tickets](docs/TODO.md) | Ordered work, dependencies, and acceptance criteria; `/to-tickets` delivery. |
| [Evidence and Limits](docs/RESEARCH.md) | Local inspection, consulted sources, and unconfirmed questions. |
| [Implementation](docs/IMPLEMENTATION.md) | How to run, resource consumption limits, and what is still missing. |

The `/to-spec` and `/to-tickets` commands were interpreted as local document deliverables. No tickets were published to an external service.
