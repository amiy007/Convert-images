from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image, ImageSequence
import pillow_avif
import io
from flask_cors import CORS
bytesgif2avifHTML = Flask(__name__)

CORS(bytesgif2avifHTML)


@bytesgif2avifHTML.route('/')
def index():
    return render_template('upload.html')


@bytesgif2avifHTML.route('/convert', methods=['POST'])
def convert_gif_to_avif():
    try:
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file provided"}), 400

        gif_bytes = file.read()
        gif_stream = io.BytesIO(gif_bytes)

        with Image.open(gif_stream) as im:
            if im.format != 'GIF':
                return jsonify({"error": "File is not a GIF"}), 400

            frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
            avif_bytes = io.BytesIO()
            frames[0].save(avif_bytes, format='AVIF', save_all=True, append_images=frames[1:],
                           duration=im.info.get('duration', 0), loop=0)
            avif_bytes.seek(0)
            return send_file(avif_bytes, mimetype='image/avif')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    bytesgif2avifHTML.run(debug=True)
