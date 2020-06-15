import numpy as np
import cv2
import bezier

def opencv_example(bez, shape, fac = 3):
    img = np.zeros(shape, dtype=np.float)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            img[y, x] = bez.distance2((x, y))
        print(y, "/", shape[0])

    img = np.power(img, 1/3)
    img = ((1-(img / np.max(img)))*255).astype(np.uint8)    
    img = np.flip(img, axis=0)
    resized_image = cv2.resize(img, (shape[1]*fac, shape[0]*fac), interpolation=cv2.INTER_NEAREST)
    cv2.imshow("distance", resized_image)
    cv2.waitKey(0)


if __name__ == '__main__':
    # Create a Bezier object with four control points.
    points = np.array([[0, 0], [0, 1], [1,.8], [1.5,1]]).astype(np.float32)
    points *= 50
    points += 10
    bez = bezier.Bezier(points)
    
    opencv_example(bez, shape = (80, 110))
