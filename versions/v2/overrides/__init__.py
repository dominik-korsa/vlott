import os
import csv
import logging
import json

from utils.cache.timed import timed_lru_cache
from versions.v2.schema import TTeacher


@timed_lru_cache(seconds=60*60*24)
def parse():
	"""
	Parse tables generated by tools/ggroup_conv.py
	Expects a file on path "versions/v2/overrides/gdata.tsv".
	Overrides are added to "versions/v2/overrides/teachers.json" as a typical
	key-value dictionary.
	"""
	if not os.path.exists("versions/v2/overrides/gdata.tsv"):
		logging.info("file \"versions/v2/overrides/gdata.tsv\" not found, "
		             "names will be inconsistent")
		return dict()

	fh = open("versions/v2/overrides/gdata.tsv", "r")
	table: dict[str, TTeacher] = {}

	if os.path.exists("versions/v2/overrides/teachers.json"):
		ovr = open("versions/v2/overrides/teachers.json", "r")
		for k,v in json.load(ovr).items():
			table[k.lower()] = TTeacher(name=v.name, short=v.short)

	for _, name in csv.reader(fh, delimiter=";"):
		fname, sname = name.split()
		teacher = TTeacher(name=name, short=f"{fname[0]}. {sname}")
		table[f"{sname}{fname[0]}".lower()] = teacher
		table[f"{sname}_{fname[0]}".lower()] = teacher
		table[name.lower()] = teacher

		if "-" in sname:
			for part in sname.split("-"):
				table[f"{part}_{fname[0]}".lower()] = teacher
				table[f"{part}{fname[0]}".lower()] = teacher

	fh.close()
	return table
