#import cv2
import numpy as np
import os
from tqdm import tqdm
#from skimage import io, color, morphology
from rembg import remove, new_session
from PIL import Image
from skimage import morphology


input_folder = "images"
output_folder = "output_images"

os.makedirs(output_folder, exist_ok=True)

#new
session = new_session("u2net")

for filename in tqdm(os.listdir(input_folder), desc="Processing images"):

    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    input_path = os.path.join(input_folder, filename)

    with Image.open(input_path) as img:
        #result = remove(img)
        result = remove(
            img,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )

    output_path = os.path.join(
        output_folder,
        os.path.splitext(filename)[0] + ".png"
    )

    result.save(output_path)
    # path = os.path.join(input_folder, filename)

    # img = Image.open(path).convert("RGB")

    # # AI background removal
    # result = remove(
    #     img,
    #     session=session,
    #     alpha_matting=True,
    #     # alpha_matting_foreground_threshold=240,
    #     # alpha_matting_background_threshold=10,
    #     # alpha_matting_erode_size=10
    # )

    # rgba = np.array(result)

    # # Extract alpha mask
    # alpha = rgba[:, :, 3] > 0

    # # Remove tiny artifacts
    # alpha = morphology.remove_small_objects(alpha, max_size=300)

    # # Fill holes (important for clothing gaps)
    # alpha = morphology.remove_small_holes(alpha, max_size=500)

    # # Slight smoothing of edges
    # alpha = morphology.closing(alpha, morphology.disk(10))

    # rgba[:, :, 3] = alpha.astype(np.uint8) * 255

    # output_path = os.path.join(
    #     output_folder,
    #     os.path.splitext(filename)[0] + ".png"
    # )

    # Image.fromarray(rgba).save(output_path)



print("Background removal complete!")