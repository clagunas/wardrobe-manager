from PIL import Image
from rembg import remove, new_session
import math

session = new_session("u2net")

def remove_background(input_path, output_path):

    if not input_path.lower().endswith((".png", ".jpg", ".jpeg")):
            print("Invalid image file format.")
    else:        
        with Image.open(input_path) as img:
            result = remove(
                img,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10,
            )

        #result.save(output_path)
        # Ensure image has alpha channel for transparency
        if result.mode != "RGBA":
            result = result.convert("RGBA")

        # Crop to non-transparent content
        bbox = result.getbbox()  # Bounding box of non-zero alpha pixels
        if bbox:
            cropped = result.crop(bbox)
        else:
            cropped = result  # fallback if somehow empty

        # Save the cropped image
        # or maybe just return like the other? 
        cropped.save(output_path)


def combine_images_square(paths, canvas_size=1024, bg_color="white"):
    
    paths = ["images/" + p for p in paths]
    images = [Image.open(p).convert("RGBA") for p in paths]
    n = len(images)

    # grid size
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    cell_w = canvas_size // cols
    cell_h = canvas_size // rows

    canvas = Image.new("RGB", (canvas_size, canvas_size), bg_color)

    for i, img in enumerate(images):

        # crop transparent borders 
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        # resize while keeping aspect ratio 
        img.thumbnail((cell_w, cell_h))

        r = i // cols
        c = i % cols

        # recompute position
        x = c * cell_w + (cell_w - img.width) // 2
        y = r * cell_h + (cell_h - img.height) // 2

        canvas.paste(img, (x, y), img)
    

    return canvas