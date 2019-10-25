import numpy as np
import cv2

def bbox(img):
    cols = np.any(img, axis=0)
    rows = np.any(img, axis=1)
    cmin, cmax = np.where(cols)[0][[0, -1]]
    rmin, rmax = np.where(rows)[0][[0, -1]]

    return np.array([cmin, cmax, rmin, rmax], dtype=int)


# 1. read images
# 2. crop images equally with padding
def get_clf(i=1):
    MARGIN = 40
    SEARCH = 20

    line = cv2.imread("src/line"+str(i)+".png", cv2.IMREAD_UNCHANGED).astype(float)/255
    fill = cv2.imread("src/fill"+str(i)+".png", cv2.IMREAD_UNCHANGED).astype(float)/255
    colo = fill[:]

    for img in [line, fill, colo]:
        img[:, :10, :] = 0
        img[:, -10:, :] = 0
        img[-10:, :, :] = 0
        img[:10, :, :] = 0
        

    bb = bbox(fill)
    a, b, c, d = bb + np.array([-MARGIN, MARGIN, -MARGIN, MARGIN], dtype=int)

    img = [colo, line, fill]
    for i in range(3):

        img[i] = img[i][c:d, a:b, 3]

        #cv2.imshow("win", img[i])
        #cv2.waitKey(0)
    return img
    
def generate_preview(line, fill, SEARCH=20):
    colo = fill[:]
    data = []
    coords = []
    
    for y in range(SEARCH, colo.shape[0] - SEARCH - 1):
        for x in range(SEARCH, colo.shape[1] - SEARCH - 1):
            y0, y1, x0, x1 = (y - SEARCH, y + SEARCH + 1,
                              x - SEARCH, x + SEARCH + 1)
                              
            if colo[y, x] < 1:
                patch_line = line[y0:y1, x0:x1]
                patch_fill = fill[y0:y1, x0:x1]

                if (np.max(patch_line) > 0 and np.min(patch_fill) < 1):
                    coords.append([x, y])
                    data.append([patch_line, patch_fill])
    
    return coords, data


def fill_img(coords, values, colo, line, wait=0):
    colo = colo[:]
    colo = 0.6 - colo * 0.3
    print(len(colo), len(values))

    for i in range(len(values)):
        v = float(values[i])
        x, y = coords[i]
        colo[y, x] = (colo[y, x] * (1 - v)) + (0.32 * v)

    line = 1 - np.array(line)
    colo = colo * line

    cv2.imshow("win", colo)
    cv2.waitKey(wait)
    return colo


for i in range(3):
    line, fill, colo = get_clf(i)
    coords, data = generate_preview(line, fill)

    data = np.array(data).reshape((-1, 2, 41, 41, 1))#[:5000]

    import tensorflow as tf
    model = tf.keras.models.load_model("color_model")
    new_values = np.array(model.predict(data))
    print(new_values.shape)

    np.save("values.npy", new_values)

    img = fill_img(coords, new_values, fill, line, wait=0)
    cv2.imwrite(str(i) + ".png", img)
