import numpy as np
import cv2
import scipy.ndimage
from random import random

MARGIN = 40
SEARCH = 20


FLOAT_PROB = 0.8
WHITE_PROB = 0.4 * FLOAT_PROB
BLACK_PROB = 0.3 * FLOAT_PROB


# ORDER: 'colo', 'line', 'fill'
# DATA:     [colo, line, fill] (patches)
#           result


def bbox(img):
    cols = np.any(img, axis=0)
    rows = np.any(img, axis=1)
    cmin, cmax = np.where(cols)[0][[0, -1]]
    rmin, rmax = np.where(rows)[0][[0, -1]]

    return np.array([cmin, cmax, rmin, rmax], dtype=int)


def populate_data(image_set, data=[], result=[]):
    colo, line, fill = image_set
    # cv2.imshow("win", line), cv2.waitKey(0)
    negative = 0
    positive = 0

    for y in range(SEARCH, colo.shape[0] - SEARCH - 1):
        if y%4 == 0: print(y)

        for x in range(SEARCH, colo.shape[1] - SEARCH - 1):
            y0, y1, x0, x1 = (y - SEARCH, y + SEARCH + 1,
                              x - SEARCH, x + SEARCH + 1)

            patch_line = line[y0:y1, x0:x1]
            patch_fill = fill[y0:y1, x0:x1]

            if (np.max(patch_line) > 0 and np.max(patch_fill) > 0
               and np.min(patch_fill) < 1):
                patch_colo = colo[y0:y1, x0:x1]

                val = patch_colo[SEARCH, SEARCH]

                use = False
                rn = random()
                if val == 0:
                    use = rn < BLACK_PROB
                elif val == 1:
                    use = rn < WHITE_PROB
                else: 
                    use = rn < FLOAT_PROB
                    
                if use:
                    data.append([patch_line, patch_fill])
                    result.append(patch_colo[SEARCH, SEARCH])

# 1. read images
# 2. crop images equally with padding


image = cv2.imread("src/line1.png", cv2.IMREAD_UNCHANGED)

# remove outer border
image[:, :10, :] = 0
image[:, -10:, :] = 0
image[-10:, :, :] = 0
image[:10, :, :] = 0

# Otsu's thresholding
blur_size = 5
blur = cv2.GaussianBlur(image[:, :, 3], (blur_size, blur_size), 0)
ret2, image = cv2.threshold(blur,
                            0, 255,
                            cv2.THRESH_BINARY + cv2.THRESH_OTSU)


image = image.astype(float)/255
a, b, c, d = bbox(image)
image = image[c:d, a:b]


cv2.imshow("win", image), cv2.waitKey(0)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
kernel_size = 3
kernel = np.ones((kernel_size,kernel_size),np.uint8)

#image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
#image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)


for i in range(1, 5):
    img = cv2.dilate(image, kernel, iterations = i)
    cv2.imshow("win", img), cv2.waitKey(0)
