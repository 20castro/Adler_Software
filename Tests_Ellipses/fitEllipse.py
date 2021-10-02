from header import *

def printEllipse(el):
    omega = el[0]
    a, b = el[1]
    rot = el[2]
    if b > a:
        a, b = b, a
    e = np.sqrt(1. - (b/a)**2)
    print(f'Center : ({omega[0]}, {omega[1]})')
    print(f'Axes : {a} px and {b} px giving excentricity {e}')
    print(f'Rotation angle : {rot}', end='\n\n')

def getExcentricity(path, name='Ellipse', threshold=False):
    grey_image = cv.imread(path, 0)
    if threshold:
        grey_image = cv.threshold(grey_image, 200, 255, 0)[1]
    cnt = cv.findContours(grey_image, 1, 2)[0][0]
    ellipse = cv.fitEllipse(cnt)
    
    img = cv.imread(path)
    img = cv.ellipse(img, ellipse, (255, 0, 255), 4)
    cv.imshow(name , img)
    cv.waitKey(0)
    printEllipse(ellipse)
    return cnt

def main():

    print('\n############ Clean files ############\n')
    for k in range(1, 11):
        print(f'Expected excentricity : 0.{k - 1}')
        getExcentricity('img/ellipse' + str(k) + '.png', name='Clean ellipse ' + str(k))

    print('\n############ Noised files ############\n')
    for k in range(1, 11):
        try:
            print(f'Expected excentricity : 0.{k - 1}')
            getExcentricity('img/ellipse' + str(k) + 'noise.png', name='Noise ellipse ' + str(k), threshold=True)
        except cv.error:
            print('Error occurred : bad contour\n')


if __name__ == '__main__':
    main()