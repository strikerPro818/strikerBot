import cv2
import numpy as np
import math

# Load the image of the basketball court
img = cv2.imread('/home/striker/Jetson/Xavier_NX/court1.jpg')

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply a Gaussian blur to the image
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Perform Canny edge detection on the blurred image
edges = cv2.Canny(blur, 50, 150)

# Detect the lines in the image using the Hough transform
lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)

# Draw the detected lines on the original image
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

# Extract the corners of the court by computing the intersections of the detected lines
corners = []
for i in range(len(lines)):
    for j in range(i+1, len(lines)):
        line1 = lines[i][0]
        line2 = lines[j][0]
        x1, y1 = line1[0], line1[1]
        x2, y2 = line1[2], line1[3]
        x3, y3 = line2[0], line2[1]
        x4, y4 = line2[2], line2[3]
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom != 0:
            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
            if 0 < ua < 1 and 0 < ub < 1:
                x = int(x1 + ua * (x2 - x1))
                y = int(y1 + ua * (y2 - y1))
                corners.append((x, y))

# Draw the corners on the original image
for corner in corners:
    cv2.circle(img, corner, 5, (0, 255, 0), -1)

# Draw the distances on the original image
for i in range(len(corners)):
    corner1 = corners[i]
    for j in range(i+1, len(corners)):
        corner2 = corners[j]
        distance = math.sqrt((corner2[0] - corner1[0])**2 + (corner2[1] - corner1[1])**2)
        cv2.line(img, corner1, corner2, (0, 255, 0), 2)
        cv2.putText(img, '{:.2f} px'.format(distance), ((corner1[0] + corner2[0]) // 2, (corner1[1] + corner2[1]) // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

# Display the final image with the detected lines and corners
cv2.imshow('Basketball Court', img)
cv2.waitKey(0)
cv2.destroyAllWindows()