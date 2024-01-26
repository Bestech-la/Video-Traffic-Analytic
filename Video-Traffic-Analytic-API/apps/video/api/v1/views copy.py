from datetime import datetime, timedelta
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import VideoSerializer
from apps.video.models import Video
from apps.infraction_tracker.models import InfractionTracker
from rest_framework.parsers import MultiPartParser, FormParser
import cv2
import os
import numpy as np
from PIL import Image
import tempfile
from django.core.files import File
import re
import pytesseract
from datetime import datetime
import time 
import imutils

class ListCreateAPIView(ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        video_car = cv2.VideoCapture('cars.mp4')
        print("video_car", video_car)
        video_file = self.request.data.get('video')
        yOne = self.request.data.get('yOne')
        yTwo = self.request.data.get('yTwo')
        date_time = self.request.data.get('date_time')
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')

        if video_car:
            with tempfile.NamedTemporaryFile(delete=False) as video_car:
                for chunk in video_file.chunks():
                    temp_video_file.write(chunk)
                temp_video_path = temp_video_file.name

            created_video = serializer.save()
            video_id = created_video.id

            car_cascade = cv2.CascadeClassifier('model/haarcascade_cars.xml')
            height = 720
            width = 1280

            min_width = 900
            min_height = 300

            cap = cv2.VideoCapture(temp_video_path)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

            if not os.path.exists('captured_images'):
                os.makedirs('captured_images')

            captured_car_plates = set()

            yOne = int(50)
            yTwo = int(471)
            print("yOne", yOne)
            print("yTwo", yTwo)
            red_line_y = yTwo
            green_line_y = yOne

            start_time = None

            while True:
                ret, frame = cap.read()

                if not ret:
                    break
                
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                if start_time is None:
                    start_time = current_time
                    
                timestamp = date_time + timedelta(seconds=current_time)
                print('Timestamp:', timestamp)

                cv2.line(frame, (0, red_line_y), (frame.shape[1], red_line_y), (255, 182, 193), 2)
                cv2.line(frame, (0, green_line_y), (frame.shape[1], green_line_y), (0, 255, 0), 2)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in cars:
                    if y + h > red_line_y:
                        car_id = f'{x}-{y}-{w}-{h}'
                        if car_id not in captured_car_plates:
                            text_part = ""
                            number_part = ""
                            hsv_roi = frame[y:y + h, x:x + w]

                            if y < green_line_y:
                                continue 

                            img_path_cars = f'captured_images/car_color_{str(len(os.listdir("captured_images")) + 1)}.png'
                            cv2.imwrite(img_path_cars, hsv_roi)

                            img_path_car = f'captured_images/illegal_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            plate_roi = hsv_roi[h // 3:, :]
                            cv2.imwrite(img_path_car, plate_roi)

                            image = cv2.imread(img_path_car)
                            roi_height = image.shape[0] // 5
                            roi = image[0:roi_height, :]

                            hsv_roi_car_color = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                            hist_hue = cv2.calcHist([hsv_roi_car_color], [0], None, [180], [0, 180])

                            dominant_hue = np.argmax(hist_hue)
                            dominant_color = None

                            if 0 <= dominant_hue < 15 or 160 <= dominant_hue <= 180:
                                dominant_color = "ສີແດງ"
                            elif 15 <= dominant_hue < 35:
                                dominant_color = "ສີເຫຼືອງ"
                            elif 35 <= dominant_hue < 85:
                                dominant_color = "ສີຂຽວ"
                            elif 85 <= dominant_hue < 110:
                                dominant_color = "ສີຟ້າ"
                            elif 110 <= dominant_hue < 125:
                                dominant_color = "ສີດໍາ"
                            elif 125 <= dominant_hue < 150:
                                dominant_color = "ສີເທົາ"
                            elif 150 <= dominant_hue < 180:
                                dominant_color = "ສີຂາວ"

                            hsv_car_plate = cv2.cvtColor(hsv_roi, cv2.COLOR_BGR2HSV)
                            lower_yellow = np.array([20, 100, 100])
                            upper_yellow = np.array([30, 255, 255])

                            yellow_mask = cv2.inRange(hsv_car_plate, lower_yellow, upper_yellow)

                            contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            if contours:
                                max_yellow_area = max(contours, key=cv2.contourArea)
                                x, y, w, h = cv2.boundingRect(max_yellow_area)

                                yellow_car_plate = hsv_roi[y:y + h, x:x + w]

                                if yellow_car_plate.shape[1] < min_width or yellow_car_plate.shape[0] < min_height:
                                    aspect_ratio = yellow_car_plate.shape[1] / yellow_car_plate.shape[0]
                                    new_width = min(min_width, int(min_height * aspect_ratio))
                                    new_height = min(min_height, int(min_width / aspect_ratio))
                                    yellow_car_plate = cv2.resize(yellow_car_plate, (new_width, new_height))

                                img_path = f'captured_images/yellow_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                cv2.imwrite(img_path, yellow_car_plate)

                                image_plate = cv2.imread(img_path)
                                roi_height = image_plate.shape[0] // 5
                                roi = image_plate[0:roi_height, :]

                                hsv_roi_plates_color = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                                hist_hue_plate = cv2.calcHist([hsv_roi_plates_color], [0], None, [180], [0, 180])

                                dominant_hue_plate = np.argmax(hist_hue_plate)
                                dominant_plate_color = None

                                if 0 <= dominant_hue_plate < 15 or 160 <= dominant_hue_plate <= 180:
                                    dominant_plate_color = "ສີແດງ"
                                elif 15 <= dominant_hue_plate < 35:
                                    dominant_plate_color = "ສີເຫຼືອງ"
                                elif 35 <= dominant_hue_plate < 85:
                                    dominant_plate_color = "ສີຂຽວ"
                                elif 85 <= dominant_hue_plate < 110:
                                    dominant_plate_color = "ສີຟ້າ"
                                elif 110 <= dominant_hue_plate < 125:
                                    dominant_plate_color = "ສີດໍາ"
                                elif 125 <= dominant_hue_plate < 150:
                                    dominant_plate_color = "ສີເທົາ"
                                elif 150 <= dominant_hue_plate < 180:
                                    dominant_plate_color = "ສີຂາວ"

                                image = Image.open(img_path)
                                dpi = (300, 300)
                                image.info['dpi'] = dpi
                                image.save(img_path, dpi=dpi)
                                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
                                car_info = pytesseract.image_to_string(yellow_car_plate, config=custom_config, lang='lao')
                                match = re.match(r'([ກ-ໝ]{2})(\d{4})', car_info)
                                if match:
                                    text_part = match.group(1)
                                    number_part = match.group(2)
                                    if len(text_part) == 2 and number_part.isdigit() and len(number_part) == 4:
                                        car_plate = f'{text_part} {number_part}'
                                        if car_plate not in captured_car_plates:
                                            captured_car_plates.add(car_plate)
                                            with open(img_path, 'rb') as img_file:
                                                image_file = File(img_file)
                                                report = InfractionTracker.objects.create(
                                                    vehicle_registration_number=car_plate,
                                                    vehicle_color=dominant_color,
                                                    vehicle_registration_color=dominant_plate_color,
                                                    video=created_video,
                                                    date_time=timestamp,
                                                )
                                                report.image_one.save(os.path.basename(img_path), image_file)
                                                img_file.close()
                                                print("Report saved with ID:", report.id)

                                            with open(img_path_car, 'rb') as img_file_car:
                                                image_file_car = File(img_file_car)
                                                report.image_two.save(os.path.basename(img_path_car), image_file_car)
                                                img_file_car.close()
                                                print("Car image saved for report with ID:", report.id)
                                        else:
                                            print("Image not saved (already captured):", img_path)
                                    else:
                                        print("Car information format is invalid:", car_info)
                                else:
                                    print("Car information format does not match:", car_info)

            cap.release()

class RetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = VideoSerializer

def detect_and_crop_red_plate(image_path, output_path, min_width=900, min_height=300):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"Error: Unable to read image at path {image_path}")
        print("image_path", image_path)

        # Define the color range for red plates
        lower_red = np.array([100, 50, 50])
        upper_red = np.array([1000, 255, 255])

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        red_mask = cv2.inRange(hsv, lower_red, upper_red)  
        
        # Use a closing operation to fill gaps in between object edges
        kernel = np.ones((5, 5), np.uint8)
        red_mask_closed = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(red_mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        if contours:
            max_red_area = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_red_area)

            red_car_plate = img[y:y + h, x:x + w]

            if red_car_plate.shape[1] < min_width or red_car_plate.shape[0] < min_height:
                aspect_ratio = red_car_plate.shape[1] / red_car_plate.shape[0]
                new_width = min(min_width, int(min_height * aspect_ratio))
                new_height = min(min_height, int(min_width / aspect_ratio))

                # Resize the region of the original color image
                resized_region = cv2.resize(red_car_plate, (new_width, new_height))
                
                gray_region = cv2.cvtColor(red_car_plate, cv2.COLOR_BGR2GRAY)
                gray = 'apps/image_test/gray_scale.png'
                cv2.imwrite(gray, gray_region)
                
                # Save the resized region as a new image
                cv2.imwrite(output_path, resized_region)

                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
                car_info = pytesseract.image_to_string(gray_region, config=custom_config, lang='lao')
                print(f"Detected red car plate number is:", car_info)
            else:
                print("Red car plate not detected. Resizing issue.")
        else:
            print("Red car plate not detected. Contours not found.")
    except Exception as e:
        print(f"Error: {e}")
        return

input_image_path_red = 'apps/image_test/car_color_23.png'
output_cropped_path_red = 'apps/image_test/car_color_cropped_red.png'
detect_and_crop_red_plate(input_image_path_red, output_cropped_path_red)





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


relative_path = "Video-Traffic-Analytic-API/apps/image_test/2324.png"
absolute_path = os.path.abspath(relative_path)
print(f"Absolute path: {absolute_path}")
cumulative_elapsed_total_time_pytesseract = 0


def perform_ocr():
    global cumulative_elapsed_total_time_pytesseract
    start_total_time = time.time()
    try:
        # absolute_path = os.path.abspath(image_path)
        print("absolute_path", absolute_path)
        image_path = 'apps/image_test/9510.png'
        img = Image.open(image_path)
        image = Image.open(image_path)
        dpi = (300, 300)
        image.info['dpi'] = dpi
        image.save(image_path, dpi=dpi)
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
        car_info = pytesseract.image_to_string(image_path, config=custom_config, lang='lao')
        print(f"OCR result: {car_info}")
        return car_info
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None
    finally:
        end_total_time = time.time()
        elapsed_total_time = end_total_time - start_total_time
        cumulative_elapsed_total_time_pytesseract += elapsed_total_time
        print(f"Total processing time: {elapsed_total_time} seconds")
        print(f"Cumulative elapsed total time: {cumulative_elapsed_total_time_pytesseract} seconds")

perform_ocr()

# image_folder = "Video-Traffic-Analytic-API/apps/image_test/"
# image_extension = ".png"

# if os.path.exists(image_folder):
#     for filename in os.listdir(image_folder):
#         if filename.endswith(image_extension):
#             image_path = os.path.join(image_folder, filename)
#             result = perform_ocr(image_path)
#             print(f"OCR result for {image_path}: {result}")
# else:
#     print(f"The folder {image_folder} does not exist.")
# def resize_and_save(image_path, output_path, min_width, min_height):
#     try:
#         # Read the image
#         img = cv2.imread(image_path)

#         if img is None:
#             print(f"Error: Unable to read image at path {image_path}")
#             return None

#         # Apply resize
#         resized_img = cv2.resize(img, (min_width, min_height))

#         # Save the resized image
#         cv2.imwrite(output_path, resized_img)

#         return output_path
#     except Exception as e:
#         print(f"Error during image resizing: {e}")
#         return None

# # Example usage:
# input_image_path = 'apps/image_test/9800.png'
# output_image_path = 'apps/image_test/resized_images/89800_resized.png'
# min_width = 300
# min_height = 150

# resized_path = resize_and_save(input_image_path, output_image_path, min_width, min_height)
# if resized_path:
#     print(f"Image resized and saved successfully at: {resized_path}")
# else:
#     print("Image resizing failed.")
    
# def crop_image(image_path, output_path, x, y, width, height):
#     print("image_path", image_path)
#     try:
#         # Read the image
#         img = cv2.imread(image_path)

#         if img is None:
#             print(f"Error: Unable to read image at path {image_path}")
#             return None

#         # Print image dimensions
#         print(f"Image Dimensions: {img.shape}")

#         # Check if the crop coordinates are within the image dimensions
#         if x < 0 or y < 0 or x + width > img.shape[1] or y + height > img.shape[0]:
#             print("Error: Invalid crop coordinates. Check the specified values.")
#             return None

#         # Crop the image
#         cropped_img = img[y:y + height, x:x + width]

#         # Save the cropped image
#         cv2.imwrite(output_path, cropped_img)

#         return output_path
#     except Exception as e:
#         print(f"Error during image cropping: {e}")
#         return None

# # Example usage with adjusted crop coordinates:
# input_image_path = 'apps/image_test/car_color_42.png'
# output_image_path = 'apps/image_test/cropped_images/car_color_42.png'

# # Adjusted crop coordinates within the valid range
# crop_x = 10
# crop_y = 5
# crop_width = 30
# crop_height = 20

# cropped_path = crop_image(input_image_path, output_image_path, crop_x, crop_y, crop_width, crop_height)
# if cropped_path:
#     print(f"Image cropped and saved successfully at: {cropped_path}")
# else:
#     print("Image cropping failed.")