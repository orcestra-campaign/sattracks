import re
from pathlib import Path
from collections import defaultdict
import jinja2
import pandas as pd
import datetime

srcdir = Path(__file__).parent
rootdir = srcdir.parent
templatedir = srcdir / "templates"
file_re = re.compile("PERCUSION_ORBIT_FCST_(?P<sat>[^_]+)_ORBLTP_CAPE_VERDE_ROI_V(?P<day>[0-9]{8})_F(?P<forecast_day>[0-9]{8}).txt")

def get_predictions(rootdir):
    for fn in rootdir.glob("**/*.txt"):
        if m := file_re.match(fn.name):
            entry = {
                "sat": m.group("sat"),
                "forecast_day": datetime.datetime.strptime(m.group("forecast_day"), "%Y%m%d").date(),
                "valid_day": datetime.datetime.strptime(m.group("day"), "%Y%m%d").date(),
                "forecast_file": fn.relative_to(rootdir),
            }
            kml_candidate = fn.with_suffix(".kml")
            if kml_candidate.exists():
                entry["kml_file"] = kml_candidate.relative_to(rootdir)
            yield entry


def main():
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templatedir),
            autoescape=jinja2.select_autoescape()
        )

    avail = pd.DataFrame.from_records(get_predictions(rootdir))
    avail.to_csv(rootdir / "index.csv", index=False)

    template = env.get_template("index.html")
    with open(rootdir / "index.html", "w") as outfile:
        outfile.write(template.render(avail=avail))


if __name__ == "__main__":
    exit(main())
