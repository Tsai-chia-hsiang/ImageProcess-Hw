import numpy as np
from .cimgcvtr import supportdomain

rgb = supportdomain.rgb
hsi = supportdomain.hsi

class HistogramEqualizer :
    
    def __init__(self) -> None:
        pass
    
    def transform(self, img:np.ndarray, spatial="global", needhist=False, **kwarg)->np.ndarray:

        if spatial == "global":
            return self.__global_hiseq(
                img=img,need_hist=needhist
            )
        elif spatial == "local":
            return self.__local_hiseq(
                img = img,need_hist=needhist, 
                bsize=kwarg['bsize']
            )

    def __count(self, img:np.ndarray)->np.ndarray:
        """
        return p[rk] = nk
        """ 
        p = np.bincount(img.flatten(), minlength=256)
        return p
    
    def __hiseq(self,img:np.ndarray)->np.ndarray:

        p = self.__count(img=img)
        cdf= np.cumsum(p/img.size)
        hist = (np.clip(cdf*255, 0, 255)).astype(np.uint8)
        return p, hist
    
    def __global_hiseq(self, img:np.ndarray, need_hist=False)->tuple:
        
        h0, histogram = self.__hiseq(img=img)
        m,n = img.shape
        img_hiseq = np.zeros((m*n), dtype=np.uint8)
        for i,pi in enumerate(img.flatten()):
            img_hiseq[i] = histogram[pi]
        
        img_hiseq = img_hiseq.reshape((m,n))
       
        if not need_hist:
            return img_hiseq
        
        return {
            'origin':h0.astype(np.uint16).tolist(), 
            'transform':self.__count(img_hiseq).astype(np.uint16).tolist()
        }, img_hiseq

    def __local_hiseq(self, img:np.ndarray,bsize:int, need_hist=False)->tuple:
    
        img_hiseq=np.copy(img)
        hist = []
        for i in range(0, img.shape[1], bsize):
            for j in range(0, img.shape[0], bsize):
                #print(f"{i}-{i+bsize}, {j}-{j+bsize}") 
                subimg = img[i:i+bsize, j:j+bsize]
                subimg_ = None
                if need_hist:
                    b_h0, subimg_=self.__global_hiseq(img=subimg, need_hist=need_hist)
                    hist.append(b_h0)
                else: 
                    subimg_=self.__global_hiseq(img=subimg, need_hist=need_hist)
                
                img_hiseq[i:i+bsize, j:j+bsize] = subimg_
                
        if not need_hist:
            return img_hiseq
        
        return {
            "blocks":hist, 
            "all":{
                'origin':self.__count(img).tolist(), 
                'transform':self.__count(img_hiseq).tolist()
            }
        }, img_hiseq

class ColorHistEQ(HistogramEqualizer):
    
    def __init__(self) -> None:
        super().__init__()
    
    def transform(self, img: np.ndarray, spatial="global", domain=hsi, **kwarg) -> np.ndarray:
    
        img_ = img.copy()

        if domain == hsi:
            c = [2]
            if 'required_channel' in kwarg.keys():
                c = kwarg['required_channel']
            
            for ci in c:
                img_[..., ci] =  self.__01_hist(
                    img_[..., ci], spatial=spatial, **kwarg
                )
        
        elif domain == rgb:
            if 'waring' in kwarg.keys():
                if kwarg['waring']:
                    print("Warning ! may get pesudo color")
            
            img_ = np.dstack(
                [
                    super().transform(img[..., 0],spatial),
                    super().transform(img[..., 1],spatial),
                    super().transform(img[..., 2],spatial)
                ]
            )

        return img_

    def __01_hist(self, x, spatial="global", **kwarg)->np.ndarray:
        return super().transform(
                (x*255).astype(np.uint8), spatial, **kwarg
            ).astype(np.float64)/255.0
