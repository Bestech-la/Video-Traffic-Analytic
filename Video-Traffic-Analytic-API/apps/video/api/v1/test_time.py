from datetime import datetime, timedelta
from apps.video.models import Video
import cv2
import os
import numpy as np
from PIL import Image
import tempfile
from django.core.files import File
import re
import pytesseract
from datetime import datetime


def call_image_to_text_api(result_image, lang="lao"):
    api_url = f"https://api.branah.com/api/image/imagetotext?filename={result_image}&lang={lang}"
    print(f"api_url", api_url)
    try:
        while True:
            response = requests.get(api_url)
            response.raise_for_status()
            if response.status_code == 202:
                print("Waiting for API to process image...")
                time.sleep(5)
            else:
                print(f"Processing complete")
                break
        result = response.content.encode('utf-8')
        print(f"API Response", result)
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    
cumulative_elapsed_total_time = 0
def post_image(image_file_path):
    global cumulative_elapsed_total_time
    api_url = "https://api.branah.com/api/file/upload"
    print('image not found image_file_path, image_file_path')
    start_total_time = time.time()
    try:
        if os.path.exists(image_file_path):
            with open(image_file_path, 'rb') as image_file:
                filename = {'file': (os.path.basename(image_file.name), image_file, 'image/png')}
                response = requests.post(api_url, files=filename) 
                response.raise_for_status()
                result_image = response.content.decode('utf-8') 
                call_image_to_text_api(result_image)
            return response
        else:
            print("Image file not found:", image_file_path)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    finally:
        end_total_time = time.time()
        elapsed_total_time = end_total_time - start_total_time
        cumulative_elapsed_total_time += elapsed_total_time
        print(f"Total processing time: {elapsed_total_time} seconds")
        print(f"Cumulative elapsed total time: {cumulative_elapsed_total_time} seconds")


cumulative_elapsed_total_time_pytesseract = 0
def perform_ocr(image_path):
    global cumulative_elapsed_total_time_pytesseract
    start_total_tine = time.time()
    try:
        image = Image.open(img_path)
        dpi = (300, 300)
        image.info['dpi'] = dpi
        image.save(img_path, dpi=dpi)
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
        car_info = pytesseract.image_to_string(image_path, config=custom_config, lang='lao')
        return car_info
    except Exception as e:
        print(f"Error during ORC: {e}")
        return None
    finally:
        end_total_time = time.time()
        elapsed_total_time = end_total_time - start_total_time
        cumulative_elapsed_total_time += elapsed_total_time
        print(f"Total processing time: {elapsed_total_time} seconds")
        print(f"Cumulative elapsed total time: {cumulative_elapsed_total_time} seconds")
