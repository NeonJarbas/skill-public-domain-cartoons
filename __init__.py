import random
from os.path import join, dirname

import requests
from json_database import JsonStorageXDG

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill



class PublicDomainCartoonsSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.CARTOON]
        self.skill_icon = join(dirname(__file__), "ui", "pd-cartoons.png")
        self.archive = JsonStorageXDG("PublicDomainToons", subfolder="OCP")
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._sync_db()
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        titles = []

        for url, data in self.archive.items():
            t = data["title"]
            t=t.split("|")[0].split("(")[0].replace("VHS", "").replace("High Quality", "").replace("—", "-").replace(" HD", "").replace(" HQ", "")
            if '"' in t:
                t = t.split('"')[1]
            elif "-" in t:
                t = t.split('-', 1)
                if t[1].strip().isdigit():
                    #year = t[1]
                    t = t[0]
                elif t[0].strip().isdigit():
                    #year = t[0]
                    t = t[1]
                else:
                    t = t[0]
                    #epi = t[1]
            t = t.split(" 19")[0].split("[")[0].split("(")[0].strip()
            titles.append(t)
        self.register_ocp_keyword(MediaType.CARTOON,
                                  "cartoon_name", titles)
        self.register_ocp_keyword(MediaType.CARTOON,
                                  "cartoon_streaming_provider",
                                  ["PublicDomainCartoon", "Public Domain Cartoon"])

    def _sync_db(self):
        bootstrap = "https://github.com/JarbasSkills/skill-public-domain-cartoons/raw/dev/bootstrap.json"
        data = requests.get(bootstrap).json()
        self.archive.merge(data)
        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))

    def get_playlist(self, score=50):
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": self.featured_media(),
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "title": "Public Domain Cartoons (Playlist)",
            "author": "Public Domain Cartoons"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 25 if media_type == MediaType.CARTOON else 0
        entities = self.ocp_voc_match(phrase)
        base_score += 30 * len(entities)

        title = entities.get("cartoon_name")
        skill = "cartoon_streaming_provider" in entities  # skill matched

        if title:
            base_score += 30
            candidates = [video for video in self.archive.values()
                          if title.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "artist": video["author"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.CARTOON,
                    "uri": "youtube//" + video["url"],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": video["thumbnail"],
                }

        if skill and FakeBus:
            yield self.get_playlist(base_score)

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
        } for url, video in self.archive.items()]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = PublicDomainCartoonsSkill(bus=FakeBus(), skill_id="t.fake")

    for r in s.search_db("play Felix the Cat", MediaType.CARTOON):
        print(r)
        # {'title': 'Felix the Cat COLOR CARTOON HOUR', 'artist': 'PizzaFlix', 'match_confidence': 85, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=fQzZzVzkcNs', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/fQzZzVzkcNs/sddefault.jpg?sqp=-oaymwEmCIAFEOAD8quKqQMa8AEB-AH-BIAC4AOKAgwIABABGHIgUygzMA8=&rs=AOn4CLA9Eb1UZMhN5x7LmVC5EUZBezVVbA', 'bg_image': 'https://i.ytimg.com/vi/fQzZzVzkcNs/sddefault.jpg?sqp=-oaymwEmCIAFEOAD8quKqQMa8AEB-AH-BIAC4AOKAgwIABABGHIgUygzMA8=&rs=AOn4CLA9Eb1UZMhN5x7LmVC5EUZBezVVbA'}
        # {'title': 'Felix the Cat in Bold King Cole (1936)', 'artist': 'AnimationStation', 'match_confidence': 85, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=isbzfRh4za8', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/isbzfRh4za8/hqdefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/isbzfRh4za8/hqdefault.jpg'}
        # {'title': 'PUBLIC DOMAIN CARTOON COMPILATION  # 3 - "FELIX THE CAT and his mates" VHS RIP', 'artist': 'vhs vhs', 'match_confidence': 85, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=yIkUO74QdsI', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/yIkUO74QdsI/sddefault.jpg?sqp=-oaymwEmCIAFEOAD8quKqQMa8AEB-AH-BIAC4AOKAgwIABABGHIgNyhaMA8=&rs=AOn4CLDEooS__nYTlu-l69w9g2g8TOioNA', 'bg_image': 'https://i.ytimg.com/vi/yIkUO74QdsI/sddefault.jpg?sqp=-oaymwEmCIAFEOAD8quKqQMa8AEB-AH-BIAC4AOKAgwIABABGHIgNyhaMA8=&rs=AOn4CLDEooS__nYTlu-l69w9g2g8TOioNA'}
        # {'title': 'New Superior Restoration and Color - of the Classic Cartoon Felix the Cat in Neptune Nonsense', 'artist': 'Cartoon crazys', 'match_confidence': 85, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=QP4KEEIuvCI', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/QP4KEEIuvCI/sddefault.jpg?v=60ca4e8c', 'bg_image': 'https://i.ytimg.com/vi/QP4KEEIuvCI/sddefault.jpg?v=60ca4e8c'}
        # {'title': 'Felix the Cat -  Bold King Cole (1936) | Classic cartoons', 'artist': 'Public domain cartoons', 'match_confidence': 85, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=x67uLrli920', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/x67uLrli920/hqdefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/x67uLrli920/hqdefault.jpg'}

