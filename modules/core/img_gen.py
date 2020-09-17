from PIL import Image
import os, requests

class ImageGenerator:
    def mergeImagesHorizontal(filename, images):
        minHeight = images[0].size[1]
        width = 0
        gap = 2
        for img in images:
            minHeight = min(minHeight, img.size[1])

        for img in images:
            img.thumbnail((img.size[0], minHeight), Image.HAMMING)
            width += img.size[0]

        combo = Image.new('RGB', (width+(gap*(len(images)-1)), minHeight))

        currW = 0
        for img in images:
            combo.paste(img, (currW, 0))
            currW += img.size[0] + gap

        combo.save(os.getcwd() + '/assets/img_gen/' + filename)


    def combineUrl(filename, *urls):
        images = []

        for url in urls:
            res = requests.get(url, stream=True)
            images.append(Image.open(res.raw))

        ImageGenerator.mergeImagesHorizontal(filename, images)
