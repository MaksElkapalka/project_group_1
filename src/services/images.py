import cloudinary
import cloudinary.uploader
import cloudinary.api

from src.conf.config import config



cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET
)

def edit_image(public_id, transformations):
    """
    Edits an image on Cloudinary.

    :param public_id: Public ID of the image on Cloudinary
    :param transformations: List of transformations to apply
    :return: URL of the edited image
    """
    # Формируем строку трансформаций
    transformation_string = '/'.join(transformations)
    
    # Применяем трансформации и получаем URL
    result = cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation_string)
    
    return result

def apply_filter(public_id, filter_name):
    """
    Applies a filter to an image.

    :param public_id: Public ID of the image on Cloudinary
    :param filter_name: Name of the filter to apply
    :return: URL of the edited image
    """
    return edit_image(public_id, [f"e_{filter_name}"])

def resize_image(public_id, width, height):
    """
    Changes the image size.

    :param public_id: Public ID of the image on Cloudinary
    :param width: New width
    :param height: New height
    :return: URL of the edited image
    """
    return edit_image(public_id, [f"c_scale,w_{width},h_{height}"])

def crop_image(public_id, width, height, x, y):
    """
    Crops the image.

    :param public_id: Public ID of the image on Cloudinary
    :param width: Trim width
    :param height: Crop height
    :param x: X coordinate of the start of trimming
    :param y: Y coordinate of the start of trimming
    :return: URL of the edited image
    """
    return edit_image(public_id, [f"c_crop,w_{width},h_{height},x_{x},y_{y}"])
