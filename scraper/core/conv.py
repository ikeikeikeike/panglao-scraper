def gen_mp4(src='pipe:0', dest='pipe:1'):
    return [
        'ffmpeg',
        '-y',
        '-i', src,
        '-crf', '25',
        '-preset', 'faster',
        '-f', 'mp4',
        '-movflags', 'frag_keyframe+empty_moov',
        dest
    ]


def gen_mp3(src='pipe:0', dest='pipe:1', empty=False):
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


def gen_jpg(src='pipe:0', dest='pipe:1'):
    return [
        'ffmpeg',
        '-y',
        '-ss', '61',
        '-i', src,
        '-qscale:v', '0',
        '-vframes', '1',
        dest
    ]


def gen_preview(src='pipe:0', dest='pipe:1'):
    return [
        'ffmpeg',
        '-y',
        '-ss', '60',
        '-i', src,
        '-t', '6',
        '-an',
        dest
    ]
