from flask import Flask, request, send_file
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from PIL import Image

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        base_url = request.form['base_url']
        num_images = int(request.form['num_images'])
        image_urls = [base_url.replace('1-2048.jpg', f'{i}-2048.jpg') for i in range(1, num_images + 1)]

        pdf_filename = '/tmp/output.pdf'
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        page_width, page_height = letter

        for url in image_urls:
            response = requests.get(url)
            if response.status_code == 200:
                image_filename = f'/tmp/{url.split("/")[-1]}'
                with open(image_filename, 'wb') as f:
                    f.write(response.content)

                img = Image.open(image_filename)
                img_width, img_height = img.size
                width_ratio = page_width / img_width
                height_ratio = page_height / img_height
                scale = min(width_ratio, height_ratio)
                new_width = img_width * scale
                new_height = img_height * scale
                x = (page_width - new_width) / 2
                y = (page_height - new_height) / 2

                c.drawImage(image_filename, x, y, width=new_width, height=new_height)
                c.showPage()
                os.remove(image_filename)

        c.save()
        return send_file(pdf_filename, as_attachment=True)

    return '''
    <form method="post">
        <label for="base_url">Liên kết cơ bản (có số 1):</label><br>
        <input type="text" id="base_url" name="base_url" size="50" required><br><br>
        <label for="num_images">Số lượng ảnh:</label><br>
        <input type="number" id="num_images" name="num_images" min="1" max="5" required><br><br>
        <input type="submit" value="Tải PDF">
    </form>
    '''

# Không cần hàm handler, Vercel sẽ tự xử lý qua app