import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def upload_bhog_image(file):
    """
    Upload image to Cloudinary from memory (no static folder required)
    Returns optimized and cropped URL
    """

    if not file or file.filename == "":
        return None

    # generate unique id (same concept as your Supabase version)
    unique_id = str(uuid.uuid4())

    # Upload image to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file,
        folder="bhog",
        public_id=unique_id,
        resource_type="image"
    )

    public_id = upload_result["public_id"]

    # Generate optimized URL (auto format + auto quality)
    optimized_url, _ = cloudinary_url(
        public_id,
        fetch_format="auto",
        quality="auto"
    )

    # OPTIONAL: Generate cropped version (500x500 square)
    cropped_url, _ = cloudinary_url(
        public_id,
        width=500,
        height=500,
        crop="auto",
        gravity="auto",
        fetch_format="auto",
        quality="auto"
    )

    # Choose which one to store in database:
    # return optimized_url   # best for normal use
    return optimized_url


def delete_bhog_image(image_url):
    """
    Deletes image from Cloudinary using stored URL
    """

    if not image_url:
        return

    try:
        # extract public_id from URL
        # example:
        # https://res.cloudinary.com/cloud/image/upload/bhog/abc123.jpg
        parts = image_url.split("/upload/")[1]
        public_id = parts.rsplit(".", 1)[0]

        cloudinary.uploader.destroy(public_id)

    except Exception as e:
        print("Error deleting image:", e)