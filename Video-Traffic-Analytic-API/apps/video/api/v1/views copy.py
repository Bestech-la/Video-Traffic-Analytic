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
class ListCreateAPIView(ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        video_file = self.request.data.get('video')
        yOne = self.request.data.get('yOne')
        yTwo = self.request.data.get('yTwo')
        date_time = self.request.data.get('date_time')
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')

        if video_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
                for chunk in video_file.chunks():
                    temp_video_file.write(chunk)
                temp_video_path = temp_video_file.name

            created_video = serializer.save()
            video_id = created_video.id

            # car_cascade = cv2.CascadeClassifier('model/haarcascade_eye.xml')
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

            yOne = int(yOne)
            yTwo = int(yTwo)
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

                cv2.line(frame, (0, red_line_y), (frame.shape[1], red_line_y), (0, 0, 255), 2)
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
                                continue  # Skip capturing if it's crossing a green light

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
                            # lower_yellow = np.array([20, 100, 100])
                            # upper_yellow = np.array([30, 255, 255])
                            # yellow_mask = cv2.inRange(hsv_car_plate, lower_yellow, upper_yellow)
                            # # contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            # Crop the blue car
                            lower_blue = np.array([100, 50, 50])
                            upper_blue = np.array([140, 255, 255])
                            blue_mask = cv2.inRange(hsv_car_plate, lower_blue, upper_blue)
                            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            
                            img_path_red_car = f'captured_images/red_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            cv2.imwrite(img_path_red_car, blue_mask)
                            
                            # # Save images
                            # img_path_blue_car = f'captured_images/blue_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            # cv2.imwrite(img_path_blue_car, blue_car)

                            # img_path_red_car = f'captured_images/red_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            # cv2.imwrite(img_path_red_car, red_car)

                            # img_path_yellow_info = f'captured_images/yellow_info_{str(len(os.listdir("captured_images")) + 1)}.png'
                            # cv2.imwrite(img_path_yellow_info, yellow_info)

                            # contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            # if contours:
                            #     max_yellow_area = max(contours, key=cv2.contourArea)
                            #     x, y, w, h = cv2.boundingRect(max_yellow_area)

                            #     yellow_car_plate = hsv_roi[y:y + h, x:x + w]

                            #     if yellow_car_plate.shape[1] < min_width or yellow_car_plate.shape[0] < min_height:
                            #         aspect_ratio = yellow_car_plate.shape[1] / yellow_car_plate.shape[0]
                            #         new_width = min(min_width, int(min_height * aspect_ratio))
                            #         new_height = min(min_height, int(min_width / aspect_ratio))
                            #         yellow_car_plate = cv2.resize(yellow_car_plate, (new_width, new_height))

                            #     img_path = f'captured_images/yellow_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                            #     cv2.imwrite(img_path, yellow_car_plate)
                            
                            if contours:
                                max_blue_area = max(contours, key=cv2.contourArea)
                                x_blue, y_blue, w_blue, h_blue = cv2.boundingRect(max_blue_area)

                                blue_car_plate = hsv_roi[y_blue:y_blue + h_blue, x_blue:x_blue + w_blue]

                                if blue_car_plate.shape[1] < min_width or blue_car_plate.shape[0] < min_height:
                                    aspect_ratio_blue = blue_car_plate.shape[1] / blue_car_plate.shape[0]
                                    new_width_blue = min(min_width, int(min_height * aspect_ratio_blue))
                                    new_height_blue = min(min_height, int(min_width / aspect_ratio_blue))
                                    blue_car_plate = cv2.resize(blue_car_plate, (new_width_blue, new_height_blue))

                                img_path = f'captured_images/blue_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                cv2.imwrite(img_path, blue_car_plate)

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
                                    
                                print(f"dominant_plate_color", dominant_plate_color)

                                image = Image.open(img_path)
                                dpi = (300, 300)
                                image.info['dpi'] = dpi
                                image.save(img_path, dpi=dpi)
                                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
                                car_info = pytesseract.image_to_string(blue_car_plate, config=custom_config, lang='lao')
                                match = re.match(r'([ກ-ໝ]{2})(\d{4})', car_info)
                                if match:
                                    text_part = match.group(1)
                                    number_part = match.group(2)
                                    if len(text_part) == 2 and number_part.isdigit() and len(number_part) == 4:
                                        car_plate = f'{text_part} {number_part}'
                                        print(f"car_plate", car_plate)
                                        if car_plate not in captured_car_plates:
                                            captured_car_plates.add(car_plate)
                                            with open(img_path, 'rb') as img_file:
                                                image_file = File(img_file)
                                                # timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                                report = InfractionTracker.objects.create(
                                                    vehicle_registration_number=car_plate,
                                                    vehicle_color=dominant_color,
                                                    vehicle_registration_color=dominant_plate_color,
                                                    video=created_video,
                                                    date_time=timestamp,
                                                )
                                                report.image_one.save(os.path.basename(img_path), image_file)
                                                img_file.close()
                                                # print("Report saved with ID:", report.id)

                                            with open(img_path_car, 'rb') as img_file_car:
                                                image_file_car = File(img_file_car)
                                                report.image_two.save(os.path.basename(img_path_car), image_file_car)
                                                img_file_car.close()
                                                # print("Car image saved for report with ID:", report.id)
                                    #     else:
                                    #         print("Image not saved (already captured):", img_path)
                                    # else:
                                    #     print("Car information format is invalid:", car_info)
                                # else:
                                #     print("Car information format does not match:", car_info)

            cap.release()

class RetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = VideoSerializer



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
    start_total_time = time.time()
    try:
        image = Image.open(image_path)
        dpi = (300, 300)
        image.info['dpi'] = dpi
        image.save(image_path, dpi=dpi)
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
        car_info = pytesseract.image_to_string(image_path, config=custom_config, lang='lao')
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


image_folder = "Video-Traffic-Analytic-API/apps/video/api/v1/image_test/"
image_extension = ".png"


for i in range(239, 250):
    image_path = os.path.join(image_folder, f"{i:04d}{image_extension}")
    print(f"Checking image file: {image_path}")
    if os.path.exists(image_path):
        result = perform_ocr(image_path)
        print(f"OCR result for {image_path}: {result}")
    else:
        print(f"Image file not found: {image_path}")
