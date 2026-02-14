from supabase import create_client
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)



def upload_bhog_image(file):
    if not file or file.filename == '':
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = f"bhog/{unique_name}"

    file_bytes = file.read()

    supabase.storage.from_("images").upload(
        path=file_path,
        file=file_bytes,
        file_options={
            "content-type": file.content_type
        }
    )

    return supabase.storage.from_("images").get_public_url(file_path)


def delete_bhog_image(image_url):
    """
    Deletes image from images/bhog using stored URL
    """
    # Extract path after bucket
    # example url:
    # .../object/public/images/bhog/abc123.jpg
    path = "bhog/" + image_url.split("/bhog/")[1]

    supabase.storage.from_("images").remove([path]) 