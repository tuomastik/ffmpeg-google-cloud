import io
from subprocess import Popen, PIPE

from flask import send_file


def convert_webm(request):
    if request.method != "POST":
        return "Only POST request is allowed"

    process = Popen(
        [
            "ffmpeg",
            # Input format
            "-f", "webm",
            # Input comes from pipe
            "-i", "-",
            # CRF = Constant Rate Factor.
            # Scale is 0-51, where 0 is lossless, 23 is default,
            # and 51 is worst possible. A lower value is a higher quality.
            "-crf", 23,
            # To solve this issue: https://stackoverflow.com/q/34123272
            "-movflags", "frag_keyframe+empty_moov",
            # Set pixel format. You can check the available formats of, for example,
            # H.264 video codec with the following command: ffmpeg -h encoder=libx264
            "-pix_fmt", "yuv420p",
            # Set the video codec.
            # libx264 is popular open source implementation of H.264/AVC encoding
            "-vcodec", "libx264",
            # Faster conversion
            # More information: https://superuser.com/q/490683/879860
            "-preset", "fast",
            # Specify resolution. -1 means that height will be adjusted
            # automatically preserving the aspect ratio.
            "-vf", "scale=1000:-1",
            # Overwrite output
            "-y",
            # Output format
            "-f", "mp4",
            # Output to stdout
            "-",
        ],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)

    file = request.files["file"]
    output, err = process.communicate(input=file.read())

    return send_file(io.BytesIO(output),
                     attachment_filename="video.mp4",
                     mimetype="video/mp4")
