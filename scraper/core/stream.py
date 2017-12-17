import os
import subprocess
from urllib.parse import urlsplit

from django.conf import settings

from . import conv


FNULL = None if settings.DEBUG else open(os.devnull, 'w')
PIPE = subprocess.PIPE


class Exchanger:
    """ Exchange stream to any encode """

    audio_exts = [
        'mp3', 'm4a'  # XXX: webm can use both of formats
    ]

    video_exts = [
        'mp4', 'webm', '3gp'
    ]

    def __init__(self, url, format, ext=None, **kwargs):
        self.url = url

        self._format = format
        self._ext = ext
        self._options = kwargs

    def exchange(self):
        if self._ext in self.audio_exts:
            return self._mp3()
        elif self._ext in self.video_exts:
            return self._mp4()

        return self._mp4()

    def extension(self):
        if self._ext in self.audio_exts:
            return 'mp3'
        elif self._ext in self.video_exts:
            return 'mp4'

        return 'mp4'

    def mimetype(self):
        if self._ext in self.audio_exts:
            return 'audio/mp3'
        elif self._ext in self.video_exts:
            return 'video/mp4'

        return 'video/mp4'

    def _gen_youtube(self):
        domain = "{0.netloc}".format(urlsplit(self.url))

        cmd = (f"youtube-dl '{self.url}' -f {self._format}"
               f" --hls-prefer-native -o -")

        if 'nicovideo.jp' in domain:
            return (f"{cmd}"
                    f" -u {settings.NICO_USER}"
                    f" -p {settings.NICO_PASS}")

        return cmd

    def _mp3(self):
        youtube = subprocess.Popen(
            self._gen_youtube(),
            shell=True, stdout=PIPE, stderr=None
        )

        return subprocess.Popen(
            ' '.join(conv.gen_mp3()), shell=True,
            stdin=youtube.stdout, stdout=PIPE, stderr=None
        )

    def _mp4(self):
        youtube = subprocess.Popen(
            self._gen_youtube(),
            shell=True, stdout=PIPE, stderr=None
        )

        return subprocess.Popen(
            ' '.join(conv.gen_mp4()), shell=True,
            stdin=youtube.stdout, stdout=PIPE, stderr=None
        )
