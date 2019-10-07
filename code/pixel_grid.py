import numpy as np
import cv2
import matplotlib.pyplot as plt
from tools import save_as_16bit_tiff

n_tile = 1024
tile = np.zeros(shape=(n_tile, n_tile), dtype=np.uint16)
#tile[int(n_tile/2), int(n_tile/2)] = 255

#table = np.ones(shape=(4, 4), dtype=np.uint8)

#image = np.kron(table, tile)

#plt.imshow(tile)
#plt.show()

save_as_16bit_tiff(tile, '_black')
