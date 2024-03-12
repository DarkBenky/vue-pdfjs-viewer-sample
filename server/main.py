from flask import Flask, request
from flask_cors import CORS 
import io
import base64
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def add_image_to_pdf_base64(pdf_data, image_data, left, top, width, height, page=0):
    # Create a canvas to draw the image onto
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.drawImage(io.BytesIO(image_data), left, top, width, height)
    can.save()

    print('done drawing')
    
    # Move the buffer position to the beginning
    packet.seek(0)

    # Create a PDF writer object and read the original PDF
    new_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader(io.BytesIO(pdf_data))
    output = PdfFileWriter()

    print('done creating pdfs')

    # Merge the original PDF with the new PDF containing the image
    page_obj = existing_pdf.getPage(page)
    page_obj.merge_page(new_pdf.getPage(0))
    output.addPage(page_obj)
    
    print('done merging')

    # Write the result to a new BytesIO object
    result_pdf = io.BytesIO()
    output.write(result_pdf.getvalue())
    
    print('done writing')

    # Return the BytesIO object
    return result_pdf

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Your file processing logic here
        json_data = request.get_json()
        pdfFileB64 = json_data['PdfFile'].split(',')[1]
        Overlays = json_data['Overlays']

        for overlay in Overlays:
            left, top, width, height = overlay['left'], overlay['top'], overlay['width'], overlay['height']
            img = overlay['img'].split(',')[1]
            pdfFileB64 = add_image_to_pdf_base64(pdfFileB64, img, left, top, width, height)
            print(pdfFileB64)
        
        # Save the processed PDF file
        # with open('processed.pdf', 'wb') as file:
        #     file.write(pdfFileB64.getvalue())
        
        return "File uploaded and processed successfully!"
    except Exception as e:
        print(str(e))
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)