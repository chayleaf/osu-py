# Before running the script, run this command: pip install osu.py tqdm

import osu, os, shutil
try:
	import tqdm
except:
	tqdm = None

# Config start. But the filters themselves are configured at line 58!
# Use double backslash
INPUT = 'C:\\osu!'
OUTPUT = 'C:\\Users\\pavlukivan\\code\\tmp'
# You can replace "None" with some collection name (but make sure to quote it)
COLLECTION = None
MODE = osu.Mode.STD #you can do TAIKO, MANIA, CTB
MODS = osu.Mods()
# Remove the # from some of the following lines calculate SR for these mods instead. You can combine multiple lines, like enable both DT and HR to use SR calculated for DTHR.
#MODS.EZ = True
#MODS.HT = True
#MODS.HR = True
#MODS.DT = True
# Config end

print('Loading osu!.db.')
db=osu.OsuDb(os.path.join(INPUT, 'osu!.db'))

if COLLECTION:
	colls={coll.name: coll.hashes for coll in osu.CollectionDb(os.path.join(INPUT, 'collection.db'))}
	if not COLLECTION in colls.keys():
		print("Error: couldn't find collection ", COLLECTION, '. Check your collection is EXACTLY the same as in-game (case-sensitive).', sep='')

dirs=set()

print('Loading finished. Filtering the beatmaps...')

for map in db.beatmaps:
	if map.mode != MODE or int(MODS) not in map.SR[map.mode].keys():
		continue
	if COLLECTION and map.hash not in colls[COLLECTION]:
		continue
	
	stars = map.SR[map.mode][int(MODS)]
	artist = map.artist
	title = map.title
	creator = map.creator
	diffName = map.diffName
	circleCount = map.circles
	sliderCount = map.sliders
	spinnerCount = map.spinners
	AR = map.AR
	CS = map.CS
	HP = map.HP
	OD = map.OD
	SV = map.SV
	drainTimeMs = map.drainTime
	totalTimeMs = map.totalTime
	
	#you can use any filter here. Example: if AR > 8 and creator != "Sotarks". Make sure to quote every string.
	if stars >= 5.0:
		dirs.add(map.directory)

print('Finished scanning osu!.db. Copying every mapset matching the filter...')

for folder in (tqdm.tqdm(dirs) if tqdm else dirs):
	out = os.path.join(OUTPUT, folder)
	if not os.path.isdir(out):
		shutil.copytree(os.path.join(INPUT, 'Songs', folder), out)

print('Done! Press any key to exit.')
input()
