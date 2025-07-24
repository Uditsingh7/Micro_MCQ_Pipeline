# utils/file_handler.py

import os
import random
import string
import logging

logger = logging.getLogger(__name__)

def extract_content_from_uploaded_file(uploaded_file, type_of_file):
    try:
        random_string = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        filename_parts = uploaded_file.name.split(".")
        uploaded_file_name = ".".join(filename_parts[:-1]) + random_string
        uploaded_file_name_with_extension = uploaded_file_name + "." + filename_parts[-1]
        uploaded_file_path = os.path.join("/tmp", uploaded_file_name_with_extension)

        with open(uploaded_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info("File saved to %s", uploaded_file_path)

        if type_of_file.upper() == "TEXT":
            with open(uploaded_file_path, "r", encoding="utf-8") as file:
                return file.read()

        elif type_of_file.upper() == "DOCX":
            from docx import Document
            doc = Document(uploaded_file_path)
            return "\n".join(para.text for para in doc.paragraphs)

        else:
            raise ValueError("Unsupported file type")

    except Exception as e:
        logger.exception("Error extracting content from uploaded file: %s", str(e))
        return ""
