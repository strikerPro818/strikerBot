import cv2
import numpy as np
import freenect2
# import os
# os.environ['LD_LIBRARY_PATH'] = '/path/to/freenect2/lib'

def main():
    # create the freenect2 device object
    fn = freenect2.Device()
    # start the device
    fn.start()

    while True:
        # get the color and depth frames from the device
        color_frame, depth_frame = fn.get_frames()

        # convert the color and depth frames to numpy arrays
        color_array = color_frame.asarray(np.uint8)
        depth_array = depth_frame.asarray(np.uint16)

        # perform any desired image processing here

        # display the color frame
        cv2.imshow('Color Frame', color_array)

        # wait for a key press and check for exit condition
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # release the device and close the windows
    fn.stop()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
