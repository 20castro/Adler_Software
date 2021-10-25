from header import *

class FindEllipse:

    def filtre(self, w, h):

        '''
        Filters the appropriate ellipses detected
        '''

        almostSquare = w > 0 and .9 < h/w < 1.1
        relevantDim = (.05*self.width < w < self.width) and (.05*self.height < h < self.height)
        return almostSquare and relevantDim

    def decision(self, type: np.ndarray, MajorAxis: np.ndarray, MinorAxis: np.ndarray):

        '''
        Major axis (px)
        Minor axis (px)

        Return : boolean which tells wether the geometric features given as parameters correspond to a valid wheel
        '''

        expected = 5.*type + 1.55*(1 - type)
        majorMeter = MajorAxis/self.conversion
        minorMeter = MinorAxis/self.conversion
        eccentricity = np.abs(majorMeter - minorMeter) <= .01
        width = np.abs(majorMeter - expected) <= .01
        height = np.abs(minorMeter - expected) <= .01

        return eccentricity & width & height
    
    def __init__(self, path, conversion):

        '''
        Conversion : number of pixels per millimeter
        '''

        self.conversion = conversion
        self.gimg = cv.imread(path, 0)
        self.cimg = cv.cvtColor(self.gimg, cv.COLOR_GRAY2RGB)
        self.width, self.height = self.gimg.shape
        self.data = []

    def __fit(self, threshold):

        '''
        For a given threshold, extracts the appropriate geometric features
        '''
        
        ellipses = []
        _, img = cv.threshold(self.gimg, threshold, 255, 0)
        contours, _ = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            if cnt.shape[0] > 4:
                el = cv.fitEllipse(cnt)
                (cx, cy), (a, b), alpha = el
                if self.filtre(a, b):
                    if b > a:
                        a, b = b, a
                        alpha = (alpha + 90)%180
                    ellipses.append([cx, cy, a, b, alpha])

        if len(ellipses) == 2:
            I = 0
            if ellipses[0][2]*ellipses[0][3] < ellipses[0][2]*ellipses[0][3]:
                I = 1
            self.data.append([threshold, 1] + ellipses[I])
            self.data.append([threshold, 0] + ellipses[1 - I])
            return True, ellipses

        return False, []

    def __print__(self, threshold):

        '''
        If possible, prints the picture with the two ellipses found
        '''

        ret, ellipses = self.fit(threshold)
        if ret:
            for el in ellipses:
                plottable = ((el[0], el[1]), (el[2], el[3]), el[4])
                cv.ellipse(self.cimg, plottable, (255, 0, 0), 1)
            cv.imshow('Ellipses found', self.cimg)
            cv.waitKey(0)
            self.cimg = cv.cvtColor(self.gimg, cv.COLOR_GRAY2RGB)
        else:
            raise ValueError('Invalid threshold')

    def compute(self, thbeg, thend, step=1):

        '''
        Find wether the ellipse are valid for each threshold
        '''

        self.data = []
        self.thresh = []
        for th in np.arange(thbeg, thend, step):
            self.__fit(th)
        cols = ['Threshold', 'Main', 'CX', 'CY', 'MajorAxis', 'MinorAxis', 'Angle']
        self.df = pd.DataFrame(data=np.array(self.data), columns=cols)
        self.df['Category'] = self.decision(self.df['Main'], self.df['MajorAxis'], self.df['MinorAxis'])
        print(self.df)

    def thresholdRange(self):
        pass

    def delta(self, threshold):
        pass

def main(path):
    fe = FindEllipse(path, 168)
    fe.compute(90, 120)

if __name__ == '__main__':
    path = 'Vue_dessus/img/Reelles/vert.bmp'
    main(path)