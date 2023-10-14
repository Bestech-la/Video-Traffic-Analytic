import cv2
import numpy as np

# Load the image
image = cv2.imread('Video-Traffic-Analytic-API/captured_images/illegal_car_107.png')

# Define the region of interest (ROI) as the upper 1/6 portion of the image
image_height, image_width, _ = image.shape
roi_height = image_height // 5
roi = image[0:roi_height, :]

# Convert the ROI to the HSV color space
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# Calculate the histogram of colors in the ROI
hist_hue = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])

# Find the most dominant color in the ROI
dominant_hue = np.argmax(hist_hue)
dominant_color = None


# Determine the color based on the dominant hue
if 0 <= dominant_hue < 15 or 160 <= dominant_hue <= 180:
    dominant_color = "red"
elif 15 <= dominant_hue < 35:
    dominant_color = "yellow"
elif 35 <= dominant_hue < 85:
    dominant_color = "green"
elif 85 <= dominant_hue < 110:
    dominant_color = "blue"
elif 110 <= dominant_hue < 125:
    dominant_color = "black"
elif 125 <= dominant_hue < 150:
    dominant_color = "gray"
elif 150 <= dominant_hue < 180:
    dominant_color = "white"


# Display the ROI and its dominant color
cv2.imshow('ROI', roi)
print(f'Dominant Color in the ROI: {dominant_color}')

# Wait for a key press and close the windows
cv2.waitKey(0)
cv2.destroyAllWindows()
