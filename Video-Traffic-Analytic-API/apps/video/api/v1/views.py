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
import colorsys
import pytesseract

class ListCreateAPIView(ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def rgb_to_color_name(self, rgb):
        color_names = {
            (255, 0, 0): "Red",
            (0, 255, 0): "Green",
            (139, 69, 19): "Brown",
            (128, 128, 128): "Grey",
            (0, 0, 255): "Blue",
            (255, 255, 255): "White",
            (255, 255, 0): "Yellow",
            (0, 0, 0): "Black",
        }

        min_color_diff = float("inf")
        closest_color = None
        for color, name in color_names.items():
            diff = sum((abs(color[i] - rgb[i]) for i in range(3)))
            if diff < min_color_diff:
                min_color_diff = diff
                closest_color = name

        return closest_color

    def calculate_dominant_color(self, image):
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Reshape the image to be a list of pixels
        pixels = image.reshape(-1, 3)
        
        # Convert RGB to HSV
        pixels = [colorsys.rgb_to_hsv(r / 255, g / 255, b / 255) for (r, g, b) in pixels]
        
        # Count the occurrences of each hue
        hue_counter = {}
        for (h, _, _) in pixels:
            hue = int(h * 360)
            if hue in hue_counter:
                hue_counter[hue] += 1
            else:
                hue_counter[hue] = 1
        
        # Find the dominant hue
        dominant_hue = max(hue_counter, key=hue_counter.get)
        
        # Convert dominant hue back to RGB
        r, g, b = colorsys.hsv_to_rgb(dominant_hue / 360, 1, 1)
        
        # Scale values to 0-255 and round to integers
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        
        return (r, g, b)
    
    def perform_create(self, serializer):
        video_file = self.request.data.get('video')
        yOne = self.request.data.get('yOne')
        yTwo = self.request.data.get('yTwo')
        if video_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
                for chunk in video_file.chunks():
                    temp_video_file.write(chunk)
                temp_video_path = temp_video_file.name

            # Save the video to the database first
            serializer.save()
            car_cascade = cv2.CascadeClassifier('model/haarcascade_eye.xml')
            height = 720
            width = 1280

            min_width = 900
            min_height = 300

            # Initialize video capture using the temporary video path
            cap = cv2.VideoCapture(temp_video_path)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

            # Create a directory to store captured images
            if not os.path.exists('captured_images'):
                os.makedirs('captured_images')

            # Create a set to track captured car plates
            captured_car_plates = set()

            # Define the y-coordinate of the red and green lines
            yOne = int(yOne)
            yTwo = int(yTwo) 
            red_line_y = yTwo
            green_line_y = yOne
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Draw the red line at y=500 and the green line at y=300
                cv2.line(frame, (0, (red_line_y)), (frame.shape[1], red_line_y), (0, 0, 255), 2)
                cv2.line(frame, (0, green_line_y), (frame.shape[1], green_line_y), (0, 255, 0), 2)

                # Convert the frame to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect cars in the frame
                cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in cars:
                    # Check if the car crosses the red line (y+height > red_line_y)
                    if y + h > red_line_y:
                        # Check if the car has not been captured yet
                        car_id = f'{x}-{y}-{w}-{h}'
                        if car_id not in captured_car_plates:
                            # Crop the region of interest around the car
                            text_part = ""
                            number_part = ""
                            hsv_roi = frame[y:y + h, x:x + w]

                            # Check if the car is crossing a green light (y < green_line_y)
                            if y < green_line_y:
                                continue  # Skip capturing if it's crossing a green light
                            
                            dominant_color = self.calculate_dominant_color(hsv_roi)

                            color_name = self.rgb_to_color_name(dominant_color)
                            print("Color Name:", color_name)

                            img_path_cars = f'captured_images/car_color_{str(len(os.listdir("captured_images")) + 1)}.png'
                            cv2.imwrite(img_path_cars, hsv_roi)

                            img_path_car = f'captured_images/illegal_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            plate_roi = hsv_roi[h // 3:, :]
                            cv2.imwrite(img_path_car, plate_roi)

                            hsv_car_plate = cv2.cvtColor(hsv_roi, cv2.COLOR_BGR2HSV)

                            # Define the lower and upper bounds of the yellow color range
                            lower_yellow = np.array([20, 100, 100])
                            upper_yellow = np.array([30, 255, 255])

                            yellow_mask = cv2.inRange(hsv_car_plate, lower_yellow, upper_yellow)

                            # Find contours in the yellow mask
                            contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            if contours:
                                # Find the largest yellow region (assumed to be the car plate)
                                max_yellow_area = max(contours, key=cv2.contourArea)
                                x, y, w, h = cv2.boundingRect(max_yellow_area)

                                # Crop and save only the yellow car plate
                                yellow_car_plate = hsv_roi[y:y + h, x:x + w]

                                if yellow_car_plate.shape[1] < min_width or yellow_car_plate.shape[0] < min_height:
                                    aspect_ratio = yellow_car_plate.shape[1] / yellow_car_plate.shape[0]
                                    new_width = min(min_width, int(min_height * aspect_ratio))
                                    new_height = min(min_height, int(min_width / aspect_ratio))
                                    yellow_car_plate = cv2.resize(yellow_car_plate, (new_width, new_height))

                                img_path = f'captured_images/yellow_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                cv2.imwrite(img_path, yellow_car_plate)

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
                                                report = InfractionTracker.objects.create(vehicle_registration_number=car_plate, vehicle_registration_color=color_name)
                                                report.image_one.save(os.path.basename(img_path), image_file)
                                                img_file.close()
                                                os.remove(img_path)
                                                print("Report saved with ID:", report.id)

                                            with open(img_path_car, 'rb') as img_file_car:
                                                image_file_car = File(img_file_car)
                                                report.image_two.save(os.path.basename(img_path_car), image_file_car)
                                                img_file_car.close()
                                                os.remove(img_path_car)
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
