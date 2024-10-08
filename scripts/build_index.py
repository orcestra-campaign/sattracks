import re
from pathlib import Path
from collections import defaultdict
import jinja2
import pandas as pd
import datetime

srcdir = Path(__file__).parent
rootdir = srcdir.parent
templatedir = srcdir / "templates"
file_re = re.compile("PERCUSION_ORBIT_FCST_(?P<sat>[^_]+)_ORB(?P<kind>[A-Z]+)_(?P<roi>[A-Z_]+)_ROI(?:_(?P<extra_roi>[A-Z]+))?_V(?P<day>[0-9]{8})_F(?P<forecast_day>[0-9]{8}).txt")

def get_predictions(rootdir):
    for fn in rootdir.glob("20*/**/*.txt"):
        if m := file_re.match(fn.name):
            roi = m.group("roi")
            if extra_roi := m.group("extra_roi"):
                roi += "_" + extra_roi

            entry = {
                "sat": m.group("sat"),
                "forecast_day": datetime.datetime.strptime(m.group("forecast_day"), "%Y%m%d").date(),
                "valid_day": datetime.datetime.strptime(m.group("day"), "%Y%m%d").date(),
                "kind": m.group("kind"),
                "roi": roi,
                "forecast_file": fn.relative_to(rootdir),
            }
            kml_candidate = fn.with_suffix(".kml")
            if kml_candidate.exists():
                entry["kml_file"] = kml_candidate.relative_to(rootdir)
            yield entry
        else:
            fn_rel = fn.relative_to(rootdir)
            print(f"WARNING: couldn't match pattern for file {fn_rel}")


def main():
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templatedir),
            autoescape=jinja2.select_autoescape()
        )

    avail = pd.DataFrame.from_records(get_predictions(rootdir))
    avail[avail.roi=="CAPE_VERDE"][["sat", "forecast_day", "valid_day", "kind", "forecast_file"]].to_csv(rootdir / "index.csv", index=False)  # v1: only for cape verde
    avail.to_csv(rootdir / "index_v2.csv", index=False)  # v2: includes multiple ROIs

    template = env.get_template("index.html")
    with open(rootdir / "index.html", "w") as outfile:
        outfile.write(template.render(avail=avail))


if __name__ == "__main__":
    exit(main())
