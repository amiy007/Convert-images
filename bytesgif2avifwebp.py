from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageSequence
import pillow_avif
import io

bytesgif2avifwebp= Flask(__name__)

@bytesgif2avifwebp.route('/convert/avif', methods=['POST'])
def convert_gif_to_avif():
    return convert_gif('AVIF')

@bytesgif2avifwebp.route('/convert/webp', methods=['POST'])
def convert_gif_to_webp():
    return convert_gif('WEBP')

def convert_gif(format):
    try:
        gif_bytes = request.get_data()
        if not gif_bytes:
            return jsonify({"error": "No data received"}), 400

        # Convert the bytes to a PIL Image
        gif_stream = io.BytesIO(gif_bytes)
        with Image.open(gif_stream) as im:
            # Check if the file is a GIF
            if im.format != 'GIF':
                return jsonify({"error": "File is not a GIF"}), 400

            frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
            image_bytes = io.BytesIO()
            frames[0].save(image_bytes, format=format, save_all=True, append_images=frames[1:], duration=im.info.get('duration', 0), loop=0)
            image_bytes.seek(0)

            return send_file(image_bytes, mimetype=f'image/{format.lower()}', as_attachment=True, download_name=f'output.{format.lower()}')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    bytesgif2avifwebp.run(debug=True)
