import numpy as np

class DomainConvertor():
    
    def __init__(self) -> None:

        self.__eps = np.float64(1e-17)
        self.__converter = {
            "rgb2hsi":self.__rgb2hsi,
            "hsi2rgb":self.__hsi2rgb,
            "rgb2lab":self.__rgb2lab,
            "lab2rgb":self.__lab2rgb
        }
    
    def convert(self, img, fromD, toD):
    
        if fromD == toD:
            return img
    
        c = f"{fromD}2{toD}"
        #print(c)
        return self.__converter[c](img)
    
    def __rgb2hsi(self, img:np.ndarray):

            rgb = img.astype(np.float64) / 255.0
            # 0: R, 1:G, 2:B
            R, G, B = 0, 1, 2
            DRG = rgb[..., R] - rgb[..., G]
            DRB = rgb[..., R] - rgb[..., B]
            DGB = rgb[..., G] - rgb[..., B]
            RGBSUM = np.sum(rgb, axis=2)
            shiftphasoridx = np.where(DGB < 0)
            as_zero_theta = np.where((DRG**2 + (DRB) * (DGB)) == 0.0)
            H = np.arccos(
                0.5 * (DRG + DRB) / (
                    (DRG**2 + (DRB) * (DGB)) ** 0.5 + self.__eps
                )
            )
            H[shiftphasoridx] = 2 * np.pi - H[shiftphasoridx]
            H[as_zero_theta] = 0
            I = (RGBSUM) / 3
            S = 1 - (3 / (RGBSUM + self.__eps)) * np.min(rgb, axis=2)
            return np.dstack((H, S, I))

    def __hsi2rgb(self, img:np.ndarray):
            
        def cvt(h0,s,i, theta):
            h = h0 - theta
            C0 = i*(1-s)
            C1 = i*(1+s*np.cos(h)/np.cos(np.pi/3 - h))
            C2 = 3*i - (C0 + C1)
            return (C0, C1, C2)
            
        H = img[..., 0]
        S = img[..., 1]
        I = img[..., 2]
        R = np.zeros(H.shape)
        B = R.copy()
        G = R.copy()
        theta_upper = np.arange(1, 4)
        theta_lower = np.arange(3)
        for l, u in zip(theta_lower, theta_upper):
            mask = None
            ltheta =l*2*np.pi/3
            utheta =u*2*np.pi/3
            if u == 3:
                mask = np.where((H>=ltheta) & (H<=utheta))
            else:
                mask = np.where((H>=ltheta) & (H<utheta)) 
            C0, C1, C2 = cvt(H[mask], S[mask], I[mask], theta=ltheta)
            
            if l == 0:
                R[mask],G[mask],B[mask] = C1, C2, C0
            elif l == 1:
                R[mask],G[mask],B[mask] = C0, C1, C2
            elif l == 2:
                R[mask],G[mask],B[mask] = C2, C0, C1
        
        return np.dstack(
             (np.clip(R*255, 0 ,255).astype(np.uint8),
              np.clip(G*255, 0 ,255).astype(np.uint8),
              np.clip(B*255, 0 ,255).astype(np.uint8))
            )
        
    def __rgb2lab(self, img:np.ndarray):
            pass
        
    def __lab2rgb(self, img:np.ndarray):
            pass


    