import numpy as np
import cv2
import matplotlib.pyplot as plt
from tools import save_single_for_ndarray

n_tile = 91
tile = np.zeros(shape=(n_tile, n_tile), dtype=np.uint8)
tile[int(n_tile/2), int(n_tile/2)] = 255

table = np.ones(shape=(4, 4), dtype=np.uint8)

image = np.kron(table, tile)

plt.imshow(image)
plt.show()

save_single_for_ndarray(image, 'grid.png')
