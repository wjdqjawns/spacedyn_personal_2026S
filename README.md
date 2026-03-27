# Satellite Orbit Propagator MVP

This MVP focuses only on the **orbit layer**.
It loads a TLE, propagates the orbit with **SGP4**, converts the result to an Earth-fixed frame for latitude/longitude/altitude, and saves simple visualizations.

## What this version does
- Read a TLE file
- Propagate position/velocity at fixed UTC time steps
- Return SGP4 output in TEME coordinates
- Apply a simple TEME->ECEF rotation using Greenwich sidereal time
- Convert ECEF to geodetic latitude / longitude / altitude (WGS-84)
- Save CSV logs
- Save a 3D orbit plot and a ground-track plot

## Important note about frames
The `sgp4` package returns position and velocity in the **TEME** frame, not a standard ECEF or geodetic frame.
This MVP uses a practical **approximate rotation** based on Greenwich sidereal time to produce ECEF-like coordinates for quick visualization.
That is good for a first pipeline and debugging, but for higher-accuracy downstream work you should later replace this with a more rigorous TEME->ITRF/ECEF conversion chain.

## Project layout
```text
satellite_propagator_mvp/
├── assets/
│   └── tle/
├── config/
│   └── orbit/
├── scripts/
├── src/
│   └── satsim/
└── experiments/
```

## Install
```bash
python -m pip install -r requirements.txt
```

## Prepare a TLE file
Put a 3-line TLE file in `assets/tle/`.
Example format:
```text
ISS (ZARYA)
1 xxxxxU xxxxxA   xxxxx.xxxxxxxx  .xxxxxxxx  xxxxx-0  xxxxx-0 0  999x
2 xxxxx  xx.xxxx xxx.xxxx xxxxxxx xxx.xxxx xxx.xxxx xx.xxxxxxxxxxxxx
```

A default config file is already included. Update the `tle_file` path if needed.

## Run
From the project root:
```bash
python scripts/run_orbit_case.py --config config/orbit/tle_case.yaml
```

## Outputs
Results are written under `experiments/runs/<run_name>/`
- `orbit_log.csv`
- `orbit_3d.png`
- `ground_track.png`

## Next recommended step
After this works, the natural next module is:
1. rigorous frame handling
2. IGRF magnetic field model
3. body attitude truth
4. magnetometer truth
5. B-dot controller
