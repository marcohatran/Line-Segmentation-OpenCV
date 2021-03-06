# Importing all necessary modules
import cv2
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
import numpy as np

# Initialising Kernels to be used in the program
kernel = np.ones((3, 3), np.uint8)
kernel1 = np.ones((5, 600), np.uint8)


class LineSegment:
    # Reading and pre-processing image
    def __init__(self, file):
        img = cv2.imread(file)
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width, channels = img.shape
        _, thresh = cv2.threshold(img2, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        img3 = cv2.dilate(thresh, kernel1, iterations=1)
        img3 = cv2.erode(img3, np.ones((5, int(height/200)*100), np.uint8), iterations = 2)
        self.image = img
        self.img = img3
        cv2.imshow("Image", self.img)
        self.img2 = img2

    def connectComponents(self):
        _, marked = cv2.connectedComponents(self.img, connectivity=4)
        # Mapping each component to corresponding HSV values
        label_hue = np.uint8(179*marked/np.max(marked))
        blank_ch = 255*np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

        # Converting from HSV to BGR for display
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
        labeled_img[label_hue==0] = 0

        # Eroding Image and converting to grayscale
        labeled_img = cv2.erode(labeled_img, kernel)
        image = cv2.cvtColor(labeled_img, cv2.COLOR_BGR2GRAY)
        self.img = image

    def Watershed(self):
        # Finding Eucledian distance to determine markers
        temp = ndimage.distance_transform_edt(self.img)
        Max = peak_local_max(temp, indices=False, min_distance=30, labels=self.img)
        markers = ndimage.label(Max, structure=np.ones((3, 3)))[0]

        # Applying Watershed to the image and markers
        res = watershed(temp, markers, mask = self.img)

        # If the elements are same, they belong to the same object (Line)
        for i in np.unique(res):
            if i==0:
                continue
            mask = np.zeros(self.img2.shape, dtype="uint8")
            mask[res == i] = 255

            # detect contours in the mask and grab the largest one
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            c = max(cnts, key=cv2.contourArea)

            # Drawing a rectangle around the object
            [x, y, w, h] = cv2.boundingRect(c)
            if((w * h) > 2000):
                cv2.rectangle(self.image, (x, y), (x+w, y+h), (0, 0, 255), 2)

    def disp_image(self):
        cv2.imshow("Segmented Image", self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()