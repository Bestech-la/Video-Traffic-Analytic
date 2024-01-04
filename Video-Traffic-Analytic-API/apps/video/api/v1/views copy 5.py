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
                print('Timestamp:', timestamp)

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
                                                # os.remove(img_path)
                                                print("Report saved with ID:", report.id)

                                            with open(img_path_car, 'rb') as img_file_car:
                                                image_file_car = File(img_file_car)
                                                report.image_two.save(os.path.basename(img_path_car), image_file_car)
                                                img_file_car.close()
                                                # os.remove(img_path_car)
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






def detect_and_crop_red_car_plate(image_path, output_path):
    # Read the image
    img = cv2.imread(image_path)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for red color in HSV
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])

    # Create a mask for the red color
    red_mask = cv2.inRange(hsv, lower_red, upper_red)

    # Find contours in the red mask
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours based on contour area in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

    if contours:
        # Select the contour with the maximum area
        max_contour = contours[0]

        # Get the bounding box of the entire red car plate region
        (x, y, w, h) = cv2.boundingRect(max_contour)

        # Crop the entire red car plate region
        red_plate = img[y:y + h, x:x + w]

        # Create a mask for the black regions
        black_mask = cv2.inRange(red_plate, (0, 0, 0), (1, 1, 1))

        # Set the black regions to white in the red plate
        red_plate[black_mask == 255] = [255, 255, 255]

        # Save the processed red car plate image
        cv2.imwrite(output_path, red_plate)

        # Convert to grayscale for OCR
        red_plate_gray = cv2.cvtColor(red_plate, cv2.COLOR_BGR2GRAY)

        # Perform OCR on the processed red car plate
        text = pytesseract.image_to_string(red_plate_gray, config='--psm 11')
        print("Detected red car plate number is:", text)
    else:
        print("Red car plate not detected.")

input_image_path = 'apps/image_test/car_color_48.png'
output_cropped_path_red = 'apps/image_test/car_color_48_cropped_red_1.png'

detect_and_crop_red_car_plate(input_image_path, output_cropped_path_red)

def detect_and_crop_blue_car_plate(image_path, output_path):
    try:
        img = cv2.imread(image_path)

        if img is None:
            raise Exception(f"Error: Unable to read image at path {image_path}")
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([140, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        if contours:
            # Select the contour with the maximum area
            max_contour = contours[0]

            # Get the bounding box of the entire blue car plate region
            (x, y, w, h) = cv2.boundingRect(max_contour)

            # Crop the entire blue car plate region
            blue_plate = img[y:y + h, x:x + w]

            # Create a mask for the black regions
            black_mask = cv2.inRange(blue_plate, (0, 0, 0), (1, 1, 1))

            # Set the black regions to white in the blue plate
            blue_plate[black_mask == 255] = [255, 255, 255]

            # Save the processed blue car plate image
            cv2.imwrite(output_path, blue_plate)

            # Convert to grayscale for OCR
            blue_plate_gray = cv2.cvtColor(blue_plate, cv2.COLOR_BGR2GRAY)

            # Perform OCR on the processed blue car plate
            text = pytesseract.image_to_string(blue_plate_gray, config='--psm 11')
            print("Detected blue car plate number is:", text)
        else:
            print("Blue car plate not detected.")

    except Exception as e:
        print(f"Error: {e}")
        return

input_image_path = 'apps/image_test/car_color_49.png'
output_cropped_path_blue = 'apps/image_test/car_color_49_cropped_blue_1.png'

detect_and_crop_blue_car_plate(input_image_path, output_cropped_path_blue)


def detect_and_crop_yellow_car_plate(image_path, output_path):
    try:
        # Read the image
        img = cv2.imread(image_path)

        if img is None:
            raise Exception(f"Error: Unable to read image at path {image_path}")

        # Convert BGR to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Define the lower and upper bounds for yellow color in HSV
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])

        # Create a mask for the yellow color
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Find contours in the yellow mask
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours based on contour area in descending order
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        if contours:
            # Select the contour with the maximum area
            max_contour = contours[0]

            # Get the bounding box of the entire yellow car plate region
            (x, y, w, h) = cv2.boundingRect(max_contour)

            # Crop the entire yellow car plate region
            yellow_plate = img[y:y + h, x:x + w]

            # Create a mask for the black regions
            black_mask = cv2.inRange(yellow_plate, (0, 0, 0), (1, 1, 1))

            # Set the black regions to white in the yellow plate
            yellow_plate[black_mask == 255] = [255, 255, 255]

            # Save the processed yellow car plate image
            cv2.imwrite(output_path, yellow_plate)

            # Convert to grayscale for OCR
            yellow_plate_gray = cv2.cvtColor(yellow_plate, cv2.COLOR_BGR2GRAY)

            # Perform OCR on the processed yellow car plate
            text = pytesseract.image_to_string(yellow_plate_gray, config='--psm 11')
            print("Detected yellow car plate number is:", text)
        else:
            print("Yellow car plate not detected.")

    except Exception as e:
        print(f"Error: {e}")
        return

# Example usage:
input_image_path = 'apps/image_test/car_color_47.png'
output_yellow_plate_path = 'apps/image_test/car_color_47_cropped_yellow.png'

detect_and_crop_yellow_car_plate(input_image_path, output_yellow_plate_path)


def crop_car_plate(image_path, output_path):
    print("image_path", image_path)
    img = cv2.imread(image_path)

    # Resize the image for consistency
    img = cv2.resize(img, (620, 480))

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('apps/image_test/illegal_car_88_gray.png', gray)
    

    # Apply Gaussian Blur for additional preprocessing
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imwrite('apps/image_test/illegal_car_88_blurred.png', blurred)
    

    # Edge detection
    edged = cv2.Canny(blurred, 50, 150)
    cv2.imwrite('apps/image_test/illegal_car_88_edged.png', edged)
    
    
    # Find contours in the edged image
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_image = img.copy()
    cv2.drawContours(contours_image, contours, -1, (0, 255, 0), 2)
    cv2.imwrite('apps/image_test/illegal_car_88_contours.png', contours_image)

    
    # # Sort contours based on contour area in descending order
    # contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    # contours_image = img.copy()

    # # Draw the contours on the copied image
    # cv2.drawContours(contours_image, contours, -1, (0, 255, 0), 2)

    # # Save the contours image
    # cv2.imwrite('apps/image_test/illegal_car_888_contours.png', contours_image)

    
    screenCnt = None

    for c in contours:
        peri = cv2.arcLength(c, True)
        epsilon = 0.04 * peri  # Experiment with different values
        approx = cv2.approxPolyDP(c, epsilon, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is not None:
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [np.array(screenCnt)], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        # Find contours in the mask
        mask_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create an empty mask
        full_mask = np.zeros(gray.shape, np.uint8)

        # Draw all contours on the empty mask
        cv2.drawContours(full_mask, mask_contours, -1, 255, thickness=cv2.FILLED)

        # Bitwise AND operation to get the full car plate region
        full_plate = cv2.bitwise_and(img, img, mask=full_mask)

        # Find contours in the full_mask
        full_contours, _ = cv2.findContours(full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get the bounding box of the entire car plate region
        full_plate_box = cv2.boundingRect(np.concatenate(full_contours))

        # Crop the entire car plate region
        cropped_plate = img[full_plate_box[1]:full_plate_box[1] + full_plate_box[3],
                            full_plate_box[0]:full_plate_box[0] + full_plate_box[2]]

        # Save the cropped image
        cv2.imwrite(output_path, cropped_plate)

        # Perform OCR on the cropped plate
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
        text = pytesseract.image_to_string(cropped_plate, config=custom_config, lang='lao')
        print("Detected license plate number is:", text)
    else:
        print("Car plate not detected.")

# Example usage:
input_image_path = 'apps/image_test/car_color_48.png'
output_cropped_path = 'apps/image_test/car_color_48_cropped.png'

crop_car_plate(input_image_path, output_cropped_path)

