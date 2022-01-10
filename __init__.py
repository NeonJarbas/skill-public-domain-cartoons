from os.path import join, dirname

from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_utils.parse import fuzzy_match
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from youtube_archivist import YoutubeMonitor


class PublicDomainCartoonsSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super().__init__("Public Domain Cartoons")
        self.supported_media = [MediaType.MOVIE,
                                MediaType.GENERIC]
        self.skill_icon = join(dirname(__file__), "ui", "pd-cartoons.png")
        self.default_bg = join(dirname(__file__), "ui", "bg.jpeg")
        self.archive = YoutubeMonitor(db_name="pd_cartoons",
                                      logger=LOG,
                                      blacklisted_kwords=["Welcome to CC Cartoons!",
                                                          "Help Translate Closed Captions"])

    def initialize(self):
        bootstrap = f"https://raw.githubusercontent.com/OpenJarbas/streamindex/main/{self.archive.db.name}.json"
        self.archive.bootstrap_from_url(bootstrap)

        self.archive.setDaemon(True)
        self.archive.start()
        urls = ["https://www.youtube.com/playlist?list=PLZZoPwq38bo4CtvoUyeFCBMP7xG4nOX5R",
                "https://www.youtube.com/playlist?list=PLGmIBrtuJdtPK5BBGOznCGj-PZgGOMbWl",
                "https://www.youtube.com/playlist?list=PLuNCpTRoV_LZcK5zLARj6GQrhMjCtUeKY",
                "https://www.youtube.com/playlist?list=PLRfEQAlSINBUuWkW7OPXMYuWehSbzvJAo",
                "https://www.youtube.com/user/CCCartoons/featured",
                "https://www.youtube.com/playlist?list=PLAeYoq0n7c3YXKgMzQ__41m6nxOjveOSt"]
        for url in urls:
            self.archive.monitor(url)

    # matching
    def match_skill(self, phrase, media_type):
        score = 0
        if self.voc_match(phrase, "classic"):
            score += 30
        if self.voc_match(phrase, "cartoon") or media_type == MediaType.CARTOON:
            score += 50
        if self.voc_match(phrase, "public_domain"):
            score += 20
        return score

    def normalize_title(self, title):
        title = title.lower().strip()
        title = self.remove_voc(title, "cartoon")
        title = self.remove_voc(title, "public_domain")
        title = self.remove_voc(title, "classic")
        title = title.replace("|", "").replace('"', "") \
            .replace(':', "").replace('”', "").replace('“', "") \
            .strip()
        return " ".join(
            [w for w in title.split(" ") if w])  # remove extra spaces

    def calc_score(self, phrase, match, base_score=0):
        score = base_score
        score += 100 * fuzzy_match(phrase.lower(), match["title"].lower())
        return min(100, score)

    def get_playlist(self, score=50):
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": self.featured_media(),
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "bg_image": self.default_bg,
            "title": "Public Domain Cartoons (Playlist)",
            "author": "Public Domain Cartoons"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = self.match_skill(phrase, media_type)
        if self.voc_match(phrase, "cartoon") or media_type == MediaType.CARTOON:
            yield self.get_playlist(base_score)
        if media_type == MediaType.CARTOON:
            # only search db if user explicitly requested cartoons
            phrase = self.normalize_title(phrase)
            for url, video in self.archive.db.items():
                yield {
                    "title": video["title"],
                    "author": "Public Domain Cartoons",
                    "match_confidence": self.calc_score(phrase, video, base_score),
                    "media_type": MediaType.CARTOON,
                    "uri": "youtube//" + url,
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": self.default_bg
                }

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "image": video["thumbnail"],
            "match_confidence": 70,
            "media_type": MediaType.CARTOON,
            "uri": "youtube//" + url,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "bg_image": video["thumbnail"],
            "skill_id": self.skill_id
        } for url, video in self.archive.db.items()]


def create_skill():
    return PublicDomainCartoonsSkill()
