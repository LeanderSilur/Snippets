import numpy as np
import cv2

data = np.load("data/0_data.npy")
print(data.shape)

for img in data[0]:
    cv2.imshow("win",img)
    cv2.waitKey(0)