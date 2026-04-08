# import cv2
import numpy as np
import os
from tqdm import tqdm

# from skimage import io, color, morphology
from rembg import remove, new_session
from PIL import Image
from skimage import morphology
import argparser

# new
session = new_session("u2net")


def remove_background(input_path, output_path):
    with Image.open(input_path) as img:
        result = remove(
            img,
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,
        )

    result.save(output_path)


if "__main__" == __name__:
    '''
    Remove background from clothing item images. Can choose whether to process
    the entire folder or just a single image.
    '''

    parser = argparser.ArgumentParser(
        description="Remove background from clothing item images"
    )
    parser.add_argument(
        "--input_folder",
        type=str,
        default="preprocessed_images",
        help="Folder containing input images",
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        default="output_images",
        help="Folder to save output images",
    )
    parser.add_argument(
        "--image_filename",
        type=str,
        help="Filename of a single image to process (if not provided, processes all images in the input folder)",
    )
    args = parser.parse_args()

    os.makedirs(args.output_folder, exist_ok=True)

    if args.image_filename:

        if not args.image_filename.lower().endswith((".png", ".jpg", ".jpeg")):
            print("Invalid image file format.")
            exit(1)
        input_path = os.path.join(args.input_folder, args.image_filename)
        output_path = os.path.join(
            args.output_folder, os.path.splitext(args.image_filename)[0] + ".png"
        )
        remove_background(input_path, output_path)

    else:

        for filename in tqdm(os.listdir(args.input_folder), desc="Processing images"):

            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            input_path = os.path.join(args.input_folder, filename)
            output_path = os.path.join(
                args.output_folder, os.path.splitext(filename)[0] + ".png"
            )

            remove_background(input_path, output_path)
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
