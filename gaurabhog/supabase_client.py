from supabase import create_client
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)



def upload_course_image(file):
    if not file or file.filename == '':
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = f"courses/{unique_name}"

    file_bytes = file.read()

    supabase.storage.from_("images").upload(
        path=file_path,
        file=file_bytes,
        file_options={
            "content-type": file.content_type
        }
    )

    return supabase.storage.from_("images").get_public_url(file_path)


def delete_course_image(image_url):
    """
    Deletes image from images/courses using stored URL
    """
    # Extract path after bucket
    # example url:
    # .../object/public/images/courses/abc123.jpg
    path = "courses/" + image_url.split("/courses/")[1]

    supabase.storage.from_("images").remove([path])