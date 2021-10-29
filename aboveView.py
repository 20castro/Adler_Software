from header import *

####### Hyper-paramètres à calibrer #######

length_tol = .01 # en mm
ecc_tol = 0.1 # en mm
conversion = 837/5.24 # en px/mm
hole_lower_threshold = 90
hole_upper_threshold = 120
heel_lower_threshold = 90
heel_upper_threshold = 120

###########################################

class FindEllipse:

    def filtre(self, w, h):

        '''
        Filters the appropriate ellipses detected
        '''

        almostSquare = w > 0 and .9 < h/w < 1.1
        relevantDim = (.05*self.width < w < self.width) and (.05*self.height < h < self.height)
        return almostSquare and relevantDim

    def decision(self, type, MajorAxis, MinorAxis) -> bool:

        '''
        Major axis (px)
        Minor axis (px)

        Return : boolean which tells wether the geometric features given as parameters correspond to a valid wheel
        '''

        expected = 5.24*type + 1.54*(1 - type)
        majorMeter = MajorAxis/self.conversion
        minorMeter = MinorAxis/self.conversion
        eccentricity = np.abs(majorMeter - minorMeter) <= ecc_tol
        width = np.abs(majorMeter - expected) <= length_tol
        height = np.abs(minorMeter - expected) <= length_tol

        return eccentricity & width & height

    def reframe(self):

        '''
        Reframe the image to print it
        '''
        
        _, image = cv.threshold(self.gimg, .5*heel_lower_threshold + .5*heel_upper_threshold, 255, 0)
        dim = image.shape
        contours, h = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        
        X, Y, W, H = 0, 0, 0, 0
        
        for cnt in contours:
            x, y, w, h = cv.boundingRect(cnt)       
            if self.filtre(w, h) and w*h > W*H:
                X, Y, W, H = x, y, w, h
                
        xmin = max(0, X - 40)
        ymin = max(0, Y - 40)
        xmax = min(dim[1], X + W + 41)
        ymax = min(dim[0], Y + H + 41)
    
        return ymin, ymax, xmin, xmax
    
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

        ymin, ymax, xmin, xmax = self.reframe()

        ret, ellipses = self.__fit(threshold)
        if ret:
            for el in ellipses:
                plottable = ((el[0], el[1]), (el[2], el[3]), el[4])
                cv.ellipse(self.cimg, plottable, (255, 0, 0), 3)
                cv.circle(self.cimg, (int(el[0]), int(el[1])), 3, (0, 0, 255), 2)
            cv.imshow('Ellipses found', self.cimg[ymin:ymax, xmin:xmax, :])
            cv.waitKey(0)
            self.cimg = cv.cvtColor(self.gimg, cv.COLOR_GRAY2RGB)
        else:
            raise ValueError('Invalid threshold')

    def compute(self, thbeg, thend, step=1, furtherData=False):

        '''
        Find wether the ellipses are valid for each threshold
        '''

        self.data = []
        self.thresh = []
        for th in np.arange(thbeg, thend, step):
            self.__fit(th)
        cols = ['Threshold', 'Main', 'CX', 'CY', 'MajorAxis', 'MinorAxis', 'Angle']
        self.df = pd.DataFrame(data=np.array(self.data), columns=cols)
        if furtherData:
            self.df['Category'] = self.decision(self.df['Main'], self.df['MajorAxis'], self.df['MinorAxis'])
            print(self.df)

    def answer(self) -> bool:

        '''
        Claims wether the heel is valid or not
        '''

        self.compute(
            min(heel_lower_threshold, hole_lower_threshold),
            max(heel_upper_threshold, hole_upper_threshold),)
        HeelMask = self.df['Main'] == 1
        HoleMask = self.df['Main'] == 0
        HeelCX, HeelCY = self.df.loc[HeelMask, 'CX'].mean(), self.df.loc[HeelMask, 'CY'].mean()
        HoleCX, HoleCY = self.df.loc[HoleMask, 'CX'].mean(), self.df.loc[HoleMask, 'CY'].mean()
        HeelMajor, HeelMinor = self.df.loc[HeelMask, 'MajorAxis'].mean(), self.df.loc[HeelMask, 'MinorAxis'].mean()
        HoleMajor, HoleMinor = self.df.loc[HoleMask, 'MajorAxis'].mean(), self.df.loc[HoleMask, 'MinorAxis'].mean()

        MajorValid = self.decision(1, HeelMajor, HeelMinor)
        MinorValid = self.decision(0, HoleMajor, HoleMinor)
        concentric = np.linalg.norm(np.array([HeelCX, HeelCY]) - np.array([HoleCX, HoleCY])) <= length_tol

        return MajorValid and MinorValid and concentric

    def thresholdRange(self):
        pass

    def delta(self, threshold):
        pass

def main(path):
    fe = FindEllipse(path, conversion)
    fe.__print__(90)
    print(fe.answer())
    cv.destroyAllWindows()

if __name__ == '__main__':
    path = 'Vue_dessus/img/Reelles/retro.bmp' #Prototype/green_lum_medium/vert_1 (17).jpg'
    main(path)