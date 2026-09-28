import os, runpy, pathlib
os.environ["SPR"] = "undecided"
runpy.run_path(str(pathlib.Path(__file__).with_name("shot_spr.py")), run_name="__main__")
