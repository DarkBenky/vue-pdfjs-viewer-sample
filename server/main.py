from flask import Flask, request
from flask_cors import CORS 
import base64
import cairosvg
import fitz  # PyMuPDF
# from PIL import Image
# import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def add_image_to_page(image, x_image, y_image, image_width, image_height, pdf, page_number):
    pdf[page_number].insert_image(
        fitz.Rect(x_image, y_image, x_image + image_width, y_image + image_height), pixmap = image )
    return pdf

@app.route('/upload', methods=['POST'])
def upload():
    try:
        json_data = request.get_json()
        pdfFileB64 = base64.b64decode(json_data['PdfFile'].split(',')[1])  # Decoding base64 to bytes
        
        # Open PDF using PyMuPDF
        pdf = fitz.open(stream=pdfFileB64)
        
        Overlays = json_data['Overlays']

        for overlay in Overlays:
            left, top, width, height = overlay['left'], overlay['top'], overlay['width'], overlay['height']
            file_type , img = overlay['img'].split(',')
            img = base64.b64decode(img)  # Decoding base64 to bytes
            print('file_type', file_type)
            
            if file_type.find('svg') != -1:
                # Convert SVG to PNG
                img = cairosvg.svg2png(bytestring=img , output_height=height, output_width=width)
                # # Convert PNG bytes to PIL Image
                # img_show = Image.open(io.BytesIO(img))
                # # Display the image
                # img_show.show()
            
            #  Convert image to Pixmap format
            img = fitz.Pixmap(img)
            pdf = add_image_to_page(img, left, top, width, height, pdf, (overlay['page'] - 1))
        
        # save output file
        pdf.save("output.pdf")
        
        return "File uploaded and processed successfully!"
    except Exception as e:
        print(str(e))
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
