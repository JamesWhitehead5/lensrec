##https://gist.github.com/allskyee/7749b9318e914ca45eb0a1000a81bf56
#!/usr/bin/env python

import cv2
import numpy as np
import screeninfo
import time
import threading
from ..tools import get_image_files

####Reference: https://gist.github.com/ronekko/dc3747211543165108b11073f929b85e
class Display():
    def __init__(self):
        self._lock = threading.Lock()
        self._display_image = False #is true when the image is being displayed
        self.display_thread = threading.Thread(target=None)
        self.display_thread.start()
        self.display_thread.join()

    def start_display(self, image, scale, full_screen=False):
        self.stop_display() #this prevents more than a single display thread from running
        if full_screen:
            self.display_thread = threading.Thread(target=self.display_full_screen, args=(image, scale,))
        else:
            self.display_thread = threading.Thread(target=self.display_image, args=(image, scale,))
        self.display_thread.start()
        time.sleep(0.1) #give time for the image to open

    def stop_display(self):
        with self._lock:
            self._display_image = False
        self.display_thread.join()

    def display_full_screen(self, image, scale):
        # displays full screen
        screen = screeninfo.get_monitors()[1]
        s_w, s_h = screen.width, screen.height
        i_w, i_h, _ = np.shape(image)
        wx = float(s_w)/i_w
        hx = float(s_h)/i_h
        new_scale = min(wx, hx)
        self.display_image(image, new_scale * scale)

        return None

    def display_image(self, image, scale):
        #rotate image
        image = np.transpose(image, axes=(1, 0, 2))

        screen_id = 1 #second monitor

        # get the size of the screen
        screen = screeninfo.get_monitors()[screen_id]

        image_compound = np.zeros((screen.width, screen.height, 3), dtype='uint8')

        window_name = 'projector'
        #cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.moveWindow(window_name, screen.x + 1, screen.y + 1)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)

        print("Screen size: ({}, {})".format(screen.width, screen.height))

        nx, ny, depth = image.shape
        print("Imported image width: {}".format(nx))
        print("Imported image height: {}".format(ny))

        nx_new, ny_new = int(scale*nx), int(scale*ny)
        print("Scaled image width: {}".format(nx_new))
        print("Scaled image height: {}".format(ny_new))
        image = cv2.resize(image, (ny_new, nx_new))

        #To make the image at the center
        x_offset = int(screen.width*0.5 - nx_new/2)
        y_offset = int(screen.height*0.5 - ny_new/2)

        assert ny_new <= screen.height and nx_new <= screen.width, "Image is too big for screen"

        print("Slicing {}:{}, {}:{}".format(x_offset, (nx_new + x_offset), y_offset ,(ny_new + y_offset)))
        image_compound[x_offset:(nx_new + x_offset), y_offset:(ny_new + y_offset), :] = image

        #DEBUG
        #import matplotlib.pyplot as plt
        #plt.imshow(image_compound)
        #plt.show()

        image_compound = np.transpose(image_compound, axes=(1, 0, 2))
        cv2.imshow(window_name, image_compound)

        time_resolution = 100 #milliseconds

        with self._lock: #I think operation is atomic but it doesn't hurt to be safe in this case
            self._display_image = True

        while(self._display_image):
            cv2.waitKey(time_resolution) #display image for % milliseconds

        cv2.destroyAllWindows()

    def close(self):
        cv2.destroyAllWindows()




##
##def display_image(image, time):
##    screen_id = 1 #second monitor
##
##    # get the size of the screen
##    screen = screeninfo.get_monitors()[screen_id]
##    width, height = screen.width, screen.height
##
##    window_name = 'projector'
##    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
##    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
##    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
##                          cv2.WINDOW_FULLSCREEN)
##    cv2.imshow(window_name, image)
##    cv2.waitKey(time*1000) #display image for % milliseconds
##    cv2.destroyAllWindows()

def test_display_multithread():
    images = get_image_files("../images")
    print(images)

    d = Display()

    for image_file in [images[0]]:
        image = cv2.imread(image_file)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        print("Starting display")
        #d.start_display(image, scale=0.165*2048/1600)

        d.start_display(image, scale= 1)

        print("Displayed")
        time.sleep(100)
        print("Stopping display")
        #d.stop_display()


if __name__=="__main__":
    test_display_multithread()
