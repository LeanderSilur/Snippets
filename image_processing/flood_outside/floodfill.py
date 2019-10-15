import cv2
import numpy as np
import os

THRESHOLD = 50/255
DILATE = 5
BLUR = 3

IN_DIR = "D:/path/in"
OUT_DIR = "D:/path/out"


def alpha_over(a, b, fac = 1):
    alpha = a[:,:,3]
    alpha = alpha.reshape((*alpha.shape, 1))
    alpha = np.repeat(alpha, 4, axis=2)
    return cv2.multiply(b, 1-(alpha * fac)) + a

def get_flood(img):
    th, im_th = cv2.threshold(img[:,:,:4], 0.5, 1, cv2.THRESH_BINARY)
    im_th = im_th[:,:,3]
    im_th = np.repeat(im_th.reshape((*im_th.shape, 1)), 3, axis = 2)

    h, w = im_th.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # floodfill
    no, res, flooded, shape = cv2.floodFill(im_th, mask, (0, 0), (255, 255, 255))
    flooded = 1 - (flooded[1:-1,1:-1]).astype(np.float32)

    kernel = np.ones((DILATE,DILATE), np.uint8)
    flooded = cv2.erode(flooded, kernel, iterations=1)
    flooded = cv2.GaussianBlur(flooded,(BLUR,BLUR), 0)
    return flooded

def create_shape(flood_mask):
    shape = np.ones((*flood_mask.shape, 4), dtype=np.float32)
    shape[:,:] = flood_mask.reshape((*flood_mask.shape, 1))
    return shape

def simple_comp(img, shape):
    background = np.ones(img.shape, dtype=img.dtype) * 0.2
    background = alpha_over(shape, background)
    over = alpha_over(img, background, 1)
    return over

files = next(os.walk(IN_DIR))[2]

for file in files:
    path_in = os.path.join(IN_DIR, file)
    path_out = os.path.join(OUT_DIR, file)

    img = cv2.imread(path_in, cv2.IMREAD_UNCHANGED)
    img = img.astype(np.float32)/255

    flooded = get_flood(img)
    shape = create_shape(flooded)

    #comp = simple_comp(img, shape)
    #cv2.imshow("win", comp)
    #cv2.waitKey(0)

    shape16 = shape.copy()
    shape16[:,:,:3] = 1
    shape16 = (shape16*255*255).astype(np.uint16)
    cv2.imwrite(path_out, shape16)
