from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageSequence
import pillow_avif
import io

#python gif2avif.py
# curl -X POST -F "file=@/home/amitkumar21/Desktop/hello-hi.gif" http://127.0.0.1:5000/convert --output /home/amitkumar21/Desktop/outputpython.avif

gif2avif = Flask(__name__)


@gif2avif.route('/convert', methods=['POST'])
def convert_gif_to_avif():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.gif'):
        try:
            with Image.open(file) as im:
                frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
                avif_bytes = io.BytesIO()
                frames[0].save(avif_bytes, format='AVIF', save_all=True, append_images=frames[1:],
                               duration=im.info['duration'], loop=0)
                avif_bytes.seek(0)
                return send_file(avif_bytes, mimetype='image/avif', as_attachment=True, download_name='output.avif')
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "File is not a GIF"}), 400


if __name__ == '__main__':
    gif2avif.run(debug=True)
