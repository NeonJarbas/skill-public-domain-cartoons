import json
import shutil
from os.path import dirname, isfile

from youtube_archivist import YoutubeMonitor


archive = YoutubeMonitor(db_name="pd_cartoons",
                                      blacklisted_kwords=["Welcome to CC Cartoons!",
                                                          "Help Translate Closed Captions"])

# load previous cache
cache_file = f"{dirname(dirname(__file__))}/bootstrap.json"
if isfile(cache_file):
    try:
        with open(cache_file) as f:
            data = json.load(f)
            archive.db.update(data)
            archive.db.store()
    except:
        pass  # corrupted for some reason

    shutil.rmtree(cache_file, ignore_errors=True)

for url in ["https://www.youtube.com/playlist?list=PLZZoPwq38bo4CtvoUyeFCBMP7xG4nOX5R",
                "https://www.youtube.com/playlist?list=PLGmIBrtuJdtPK5BBGOznCGj-PZgGOMbWl",
                "https://www.youtube.com/playlist?list=PLuNCpTRoV_LZcK5zLARj6GQrhMjCtUeKY",
                "https://www.youtube.com/playlist?list=PLRfEQAlSINBUuWkW7OPXMYuWehSbzvJAo",
                "https://www.youtube.com/user/CCCartoons/featured",
                "https://www.youtube.com/playlist?list=PLAeYoq0n7c3YXKgMzQ__41m6nxOjveOSt"]:
    # parse new vids
    archive.parse_videos(url)

# save bootstrap cache
shutil.copy(archive.db.path, cache_file)
