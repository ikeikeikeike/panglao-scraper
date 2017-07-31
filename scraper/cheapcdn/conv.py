import os
import random
import string
import subprocess


from core import error as core_error


_ascii = string.ascii_uppercase + string.digits


def _gen_mp3(src, dest, empty=False):
    cmd = [
        'ffmpeg',
        '-y',
        '-i', src,
        '-codec:a', 'libmp3lame',
        '-qscale:a', '2',
        dest
    ]
    if empty:
        cmd.insert(4, '-t')
        cmd.insert(5, '1')
    return cmd


def _gen_jpg(src, dest):
    return [
        'ffmpeg',
        '-y',
        '-ss', '31',
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
        '-t', '10',
        '-an',
        dest
    ]


class Media:
    EXTENTIONS = [
        '.jpg',
        '.mp3',
        '.preview.mp4',
    ]

    def __init__(self, filename):
        #  self._stat = os.stat(filename)
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
        empty = os.path.getsize(self._filename) > 524288000  # 500MByte

        cmd = _gen_mp3(self._filename, f'{dest}.mp3', empty)
        return subprocess.run(cmd).returncode

    def conv_jpg(self):
        dest, _ = os.path.splitext(self._filename)

        cmd = _gen_jpg(self._filename, f'{dest}.jpg')
        return subprocess.run(cmd).returncode

    def conv_preview_mp4(self):
        dest, _ = os.path.splitext(self._filename)

        cmd = _gen_preview(self._filename, f'{dest}.preview.mp4')
        return subprocess.run(cmd).returncode

    def conv_all(self):
        base, _ = os.path.splitext(self._filename)
        for ext in self.EXTENTIONS:
            if not os.path.exists(f'{base}{ext}'):
                getattr(self, 'conv%s' % ext.replace('.', '_'))()

    def filenames(self):
        base, _ = os.path.splitext(self._filename)
        gene = map(lambda ext: f'{base}{ext}', self.EXTENTIONS)
        return list(gene)

    def cleanup(self):
        for filename in self.filenames():
            if os.path.exists(filename):
                os.remove(filename)
