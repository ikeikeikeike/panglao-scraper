import os
import subprocess

from django.conf import settings


FNULL = None if settings.DEBUG else open(os.devnull, 'w')
PIPE = subprocess.PIPE


class Exchanger:
    """ Exchange stream to any encode """

    audio_formats = [
        'mp3', 'dash', 'webm'
    ]

    video_formats = [
        'mp4', 'webm'
    ]

    def __init__(self, url):
        self.url = url

    def exchange(self, format=None):
        if format in self.audio_formats:
            return self._mp3()
        elif format in self.video_formats:
            return self._mp4()

        return self._mp4()

    def _mp4(self):
        youtube = subprocess.Popen(
            f"youtube-dl '{self.url}' --hls-prefer-native -o -",
            shell=True, stdout=PIPE, stderr=None
        )

        ffmpeg = subprocess.Popen(
            ("ffmpeg -i pipe:0 -crf 25 -preset faster "
             "-f mp4 -movflags frag_keyframe+empty_moov pipe:1"),
            shell=True, stdin=youtube.stdout, stdout=PIPE, stderr=None
        )

        return ffmpeg

    def _mp3(self):
        youtube = subprocess.Popen(
            f"youtube-dl '{self.url}' --hls-prefer-native -o -",
            shell=True, stdout=PIPE, stderr=None
        )

        return subprocess.Popen(
            ("ffmpeg -i pipe:0 -crf 25 -preset faster "
             "-f mp4 -movflags frag_keyframe+empty_moov pipe:1"),
            shell=True, stdin=youtube.stdout, stdout=PIPE, stderr=None
        )
