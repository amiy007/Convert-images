from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageSequence
import pillow_avif
import io

gifconvertcrop = Flask(__name__)

@gifconvertcrop.route('/convert/avif', methods=['POST'])
def convert_gif_to_avif():
    return convert_gif('AVIF')

@gifconvertcrop.route('/convert/webp', methods=['POST'])
def convert_gif_to_webp():
    return convert_gif('WEBP')

def convert_gif(format):
    try:
        gif_bytes = request.get_data()
        if not gif_bytes:
            return jsonify({"error": "No data received"}), 400

        compression_percentage = request.args.get('compression', default=100, type=int)
        resize_width = request.args.get('width', type=int)
        resize_height = request.args.get('height', type=int)
        crop_x = request.args.get('crop_x', type=int)
        crop_y = request.args.get('crop_y', type=int)
        crop_width = request.args.get('crop_width', type=int)
        crop_height = request.args.get('crop_height', type=int)

        # Convert the bytes to a PIL Image
        gif_stream = io.BytesIO(gif_bytes)
        with Image.open(gif_stream) as im:
            # Check if the file is a GIF
            if im.format != 'GIF':
                return jsonify({"error": "File is not a GIF"}), 400

            frames = [frame.copy() for frame in ImageSequence.Iterator(im)]

            # Apply resizing
            if resize_width and resize_height:
                frames = [frame.resize((resize_width, resize_height), Image.Resampling.LANCZOS) for frame in frames]

            # Apply cropping
            if crop_x is not None and crop_y is not None and crop_width and crop_height:
                frames = [frame.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height)) for frame in frames]

            # Apply compression
            quality = int(100 * (compression_percentage / 100))

            image_bytes = io.BytesIO()
            frames[0].save(image_bytes, format=format, save_all=True, append_images=frames[1:], duration=im.info.get('duration', 0), loop=0, quality=quality)
            image_bytes.seek(0)

            return send_file(image_bytes, mimetype=f'image/{format.lower()}', as_attachment=True, download_name=f'output.{format.lower()}')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    gifconvertcrop.run(debug=True)
