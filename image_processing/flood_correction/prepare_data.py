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


image_sets = []

for i in range(4):
    arr = []
    for name in ['colo', 'line', 'fill']:
        image = cv2.imread("src/" + name + str(i) + ".png",
                           cv2.IMREAD_UNCHANGED)
                           
        # remove outer border
        image[:, :10, :] = 0
        image[:, -10:, :] = 0
        image[-10:, :, :] = 0
        image[:10, :, :] = 0

        arr.append(image[:, :, 3].astype(float)/255)
    image_sets.append(arr)


for images in image_sets:
    bb = bbox(images[0])

    # apply padding
    a, b, c, d = bb + np.array([-MARGIN, MARGIN, -MARGIN, MARGIN], dtype=int)

    for i in range(len(images)):
        images[i] = images[i][c:d, a:b]

"""
        cv2.imshow("win", images[i])
        cv2.waitKey(0)
"""

test_set = image_sets.pop(1)


data = []
result = []
for i in range(0, 3):
    populate_data(image_sets[i], data, result)

data, result = np.array(data), np.array(result)
np.save("data/data.npy", data)
np.save("data/result.npy", result)
