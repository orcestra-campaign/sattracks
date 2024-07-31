import glob
import re
from pathlib import Path
from collections import defaultdict
import jinja2

srcdir = Path(__file__).parent
rootdir = srcdir.parent
templatedir = srcdir / "templates"
file_re = re.compile("PERCUSION_ORBIT_FCST_(?P<sat>[^_]+)_ORBLTP_CAPE_VERDE_ROI_(?P<forecast_day>[0-9]{8})_(?P<day>[0-9]{8}).txt")

def main():
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templatedir),
            autoescape=jinja2.select_autoescape()
        )
    avail = defaultdict(lambda: defaultdict(list))
    for fn in glob.glob(str(rootdir / "**/*.txt")):
        if m := file_re.match(fn.split("/")[-1]):
            avail[m.group("sat")][m.group("forecast_day")].append(m.group("day"))
    avail = {k: {**v} for k, v in avail.items()}

    template = env.get_template("index.html")
    with open(rootdir / "index.html", "w") as outfile:
        outfile.write(template.render(avail=avail))


if __name__ == "__main__":
    exit(main())
