import io
from typing import Tuple, List
from subprocess import Popen, PIPE

from flask import Flask, request, send_file, render_template
from flask_cors import CORS


app = Flask(__name__, template_folder=".")
# Add CORS (Cross-Origin Resource Sharing) support
CORS(app)

GIF, MP4 = "gif", "mp4"
FORMATS = [GIF, MP4]
INVALID_FORMAT = f"Only {FORMATS} formats are accepted"


@app.route("/", methods=["GET"])
def upload_form():
    return render_template("index.html")


def parse_fmt_query_param(fmt: str, crf: str) -> Tuple[List[str], str]:
    if fmt == MP4:
        fmt_specific_mimetype = "video/mp4"
        fmt_specific_ffmpeg_options = [
            # CRF = Constant Rate Factor.
            # Scale is 0-51, where 0 is lossless, 23 is default,
            # and 51 is worst possible. A lower value is a higher quality.
            "-crf", f"{crf}",
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
        ]
    elif fmt == GIF:
        fmt_specific_mimetype = "image/gif"
        fmt_specific_ffmpeg_options = []
    else:
        raise ValueError(INVALID_FORMAT)
    return fmt_specific_ffmpeg_options, fmt_specific_mimetype


@app.route("/", methods=["POST"])
def convert_webm():
    file = request.files.get("file")
    width = request.form.get("width", 500)
    crf = request.form.get("crf", 23)
    fmt = request.form.get("fmt", "gif")

    try:
        crf = int(crf)
    except ValueError:
        return "'crf' has to be integer"
    if not (0 <= crf <= 51):
        return ("'crf' needs to be in range [0, 51], where 0 is lossless, "
                "23 is default, and 51 is worst possible")

    if not fmt:
        return f"'fmt' query parameter is mandatory. Options: {FORMATS}"
    if fmt not in FORMATS:
        return INVALID_FORMAT
    fmt_specific_ffmpeg_options, fmt_specific_mimetype = parse_fmt_query_param(fmt, str(crf))

    process = Popen(
        [
            "ffmpeg",
            # Input format
            "-f", "webm",
            # Input comes from pipe
            "-i", "-",
            # Specify resolution. -1 means that height will be adjusted
            # automatically preserving the aspect ratio.
            "-vf", f"scale={width}:-1",
        ]
        + fmt_specific_ffmpeg_options +
        [
            # Output format
            "-f", f"{fmt}",
            # Output to stdout
            "-",
        ],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)

    output, err = process.communicate(input=file.read())

    if process.returncode != 0:
        return f"Oops! Something went wrong when executing ffmpeg.\n\n{err}"

    return send_file(io.BytesIO(output),
                     attachment_filename=f"video.{fmt}",
                     mimetype=fmt_specific_mimetype,
                     as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
