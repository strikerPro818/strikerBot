import cv2

cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

# print(cv2.getBuildInformation())
#
while True:
    ret, frame = cap.read()

    if ret:
        cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
