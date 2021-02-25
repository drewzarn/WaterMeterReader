import cv2
import numpy as np

img1 = cv2.imread('samples/identical1.png')
img2 = cv2.imread('samples/identical2.png')
img3 = cv2.imread('samples/identical3.png')

same = cv2.cvtColor(cv2.absdiff(img1, img2), cv2.COLOR_BGR2GRAY).astype(np.int16)
diff = cv2.cvtColor(cv2.absdiff(img1, img3), cv2.COLOR_BGR2GRAY).astype(np.int16)
sameTrimmed = (same - 5).clip(min=0)

print(cv2.countNonZero(same), cv2.countNonZero(sameTrimmed))
diffTrimmed = (diff - 5).clip(min=0)
print(cv2.countNonZero(diff), cv2.countNonZero(diffTrimmed))
#print(len(same) * len(same[0]), cv2.countNonZero(same), cv2.countNonZero(diff))

cv2.imwrite('samples/diff.png', diff)
cv2.imwrite('samples/same.png', same)