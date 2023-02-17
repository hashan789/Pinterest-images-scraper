from flask import Flask, render_template, request , send_file, send_from_directory
from datetime import date
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import os
import pinterest,pinterestImages

app = Flask(__name__)

day = date.today()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'),'favicon.ico',mimetype='image/favicon.jpg')

@app.route('/')
def index():
    if request.args.get('img'):
        name = request.args.get('img')
        response = requests.get(name)

        folder_name = "downloads/images"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        url_image = name.split("/")

        image = url_image[len(url_image) - 1]
        file_path = os.path.join(folder_name, image)

        with open(file_path, 'wb') as f:
            if f.write(response.content):
                is_downloaded = "Download completed"
            else:
                is_downloaded = "Download not completed"

        return render_template("download.html", res=is_downloaded)
    else:
        return render_template("index.html")


@app.route('/', methods=['POST'])
def getValue():
    p_scraper = pinterest.PinterestImageScraper()
    result = ''

    keyword = request.form['pinterest']
    urls = p_scraper.make_ready(keyword)

    return render_template("scrape.html", image = urls)

@app.route('/batch', methods=['POST'])
def getBatch():
    url = request.form['pinterest_link']

    try:
        source = requests.get(url)
        source.raise_for_status()

        soup = BeautifulSoup(source.text, 'html.parser')

        head_div = soup.find('img',{'class':'hCL kVc L4E MIw'})
        img = head_div.get('src')

        source_img = requests.get(img)
        resource = source_img

        url_image = img.split("/")
        image = url_image[len(url_image) - 1]
        image_path = image.split(".")[0]

        folder_name = f'downloads/{day}_{image_path}/images'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_path = os.path.join(folder_name, image)

        with open(file_path, 'wb') as f:
            if f.write(resource.content):
                is_downloaded = "Download completed"
            else:
                is_downloaded = "Download not completed"

        batch_images = pinterestImages.downloadPinterestImages(url)

        for batch in batch_images:
            source_img_batch = requests.get(batch)
            resource_batch = source_img_batch

            url_image_batch = batch.split("/")

            batch_folder_name = f'downloads/{day}_{image_path}/batch_images'
            if not os.path.exists(batch_folder_name):
                os.makedirs(batch_folder_name)

            image_batch = url_image_batch[len(url_image_batch) - 1]
            file_path_batch = os.path.join(batch_folder_name, image_batch)

            with open(file_path_batch, 'wb') as f:
                if f.write(resource_batch.content):
                    is_downloaded = "Download completed"
                else:
                    is_downloaded = "Download not completed"

        return render_template("batch.html", res=is_downloaded)
        print(img)

    except Exception as e:
        print(e)

    return 'ok'

if __name__ == '__main__':
    app.run(debug=True)
