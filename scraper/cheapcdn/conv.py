import os
import random
import string
import subprocess


from core import error as core_error


_ascii = string.ascii_uppercase + string.digits


def _gen_mp3(src, dest):
    return [
        'ffmpeg',
        '-y',
        '-i', src,
        '-codec:a', 'libmp3lame',
        '-qscale:a', '2',
        dest
    ]


def _gen_jpg(src, dest):
    return [
        'ffmpeg',
        '-y',
        '-ss', '30',
        '-i', src,
        '-qscale:v', '0',
        '-vframes', '1',
        dest
    ]


def _gen_preview(src, dest):
    return [
        'ffmpeg',
        '-y',
        '-ss', '30',
        '-i', src,
        '-t', '15',
        dest
    ]


class Media:
    def __init__(self, filename):
        self._stat = os.stat(filename)
        self._filename = filename

    def is_movie(self):
        if not self._filename:
            return False
        dest = "".join(random.choices(_ascii, k=10))
        tmpname = f'/tmp/{dest}.jpg'

        cmd = _gen_jpg(self._filename, tmpname)
        r = subprocess.run(cmd)

        with core_error.ignore(FileNotFoundError):
            os.remove(tmpname)
        return r.returncode == 0

    # def is_audio(self):
    #     if not self._filename:
    #         return False
    #     dest = "".join(random.choices(_ascii, k=10))
    #     tmpname = f'/tmp/{dest}.mp3'

    #     cmd = _gen_mp3(self._filename, tmpname, {'s': 10, 't': 10})
    #     r = subprocess.run(cmd)

    #     with core_error.ignore(FileNotFoundError):
    #         os.remove(tmpname)
    #     return r.returncode == 0

    def conv_mp3(self):
        dest, _ = os.path.splitext(self._filename)

        cmd = _gen_mp3(self._filename, f'{dest}.mp3')
        r = subprocess.run(cmd)

        return r.returncode

    def conv_jpg(self):
        dest, _ = os.path.splitext(self._filename)

        cmd = _gen_jpg(self._filename, f'{dest}.jpg')
        r = subprocess.run(cmd)

        return r.returncode

    def conv_preview(self):
        dest, _ = os.path.splitext(self._filename)

        cmd = _gen_preview(self._filename, f'{dest}-preview.mp4')
        r = subprocess.run(cmd)

        return r.returncode
