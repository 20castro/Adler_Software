from header import *

img = cv.imread('Tests_Ellipses/img/logo.png', 0)

img = cv.medianBlur(img, 5) # utilité ?

cimg = cv.imread('Tests_Ellipses/img/logo.png')

circles = cv.HoughCircles( # détection des cercles
    img,
    cv.HOUGH_GRADIENT,
    1,
    20,
    param1=50,
    param2=30,
    minRadius=0,
    maxRadius=0)
circles = np.uint16(np.around(circles)[0]) # arrondi (sinon cv2 error type)

print('List of circles following structure [xCentre, yCentre, radius]\n')
print(circles)

for i in circles:
    # draw the outer circle
    cimg = cv.circle(cimg,(i[0], i[1]), i[2], (0, 200, 200), 2)
    # draw the center of the circle
    cimg = cv.circle(cimg, (i[0], i[1]), 2,(0, 0, 255), 3)

cv.imshow('Detected circles', cimg)
cv.waitKey(0)
cv.destroyAllWindows()