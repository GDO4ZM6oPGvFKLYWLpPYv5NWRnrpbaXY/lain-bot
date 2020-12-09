from PIL import Image, ImageSequence
from itertools import zip_longest
import io, logging, asyncio
logger = logging.getLogger(__name__)

class ImageGenerator:

    @staticmethod
    def mergeImagesHorizontal(images):
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

        img_bin = io.BytesIO()
        combo.save(img_bin, format='jpeg')
        img_bin.seek(0)
        return img_bin

    @staticmethod
    async def combineUrl(session, loop, urls):
        images = []

        for url in urls:
            async with session.get(url) as resp:
                images.append(Image.open(io.BytesIO(await resp.read())))

        return await loop.run_in_executor(
            None, 
            ImageGenerator.mergeImagesHorizontal,
            images
        )

    @staticmethod
    async def get_profile_picture(session, user):
        """
        Get a bytes representation of a discord members profile picture
        """
        url = ('https://cdn.discordapp.com/avatars/{0.id}/'
            '{0.avatar}.png?size=128').format(user)
        async with session.get(url) as resp:
            return(io.BytesIO(await resp.content.read()))

    @staticmethod
    def insert_picture_in_gif(gif, ins_pic, coords) -> io.BytesIO:
        '''
        Insert a picture `ins_pic` into a gif `gif` with the upper left and
        lower right coords of the the image to be inserted on each frame as
        acollection of 4-tuples `coords`. Both `ins_pic` and `gif` must be
        able to be passed to Pillow's image open function (ex.: a path or
        byterepresentation of an image).
        '''
        frames = []
        with Image.open(gif) as im:
            with Image.open(ins_pic).convert('RGB') as ins_pic:
                for frame, coords in zip_longest(
                        ImageSequence.Iterator(im), coords):
                    frame = frame.copy().convert('RGB')
                    if coords:
                        frame.paste(ins_pic, coords)
                    frames.append(frame)

        image_bin = io.BytesIO()
        frames[0].save(image_bin, 'GIF', save_all=True,
                    append_images=frames[1:], loop=0)
        image_bin.seek(0)
        return image_bin
