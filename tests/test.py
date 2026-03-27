from spacedyn.io.tle_reader import read_tle_catalog

records = read_tle_catalog("assets/tle/sample.tle")

for r in records:
    print(r.name)