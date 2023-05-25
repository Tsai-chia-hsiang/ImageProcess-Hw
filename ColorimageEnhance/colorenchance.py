import os
import numpy as np
from tqdm import tqdm
from ColorIMGkit.cimgcvtr import DomainConvertor, supportdomain
from ColorIMGkit.histEQ import ColorHistEQ
from ColorIMGkit.sharpening import RGBSharpener
from ColorIMGkit.RGBimgIO import readimgs, saveimgs, rgbimg

rgb = supportdomain.rgb
hsi = supportdomain.hsi
lab = supportdomain.lab

convertor = DomainConvertor()
histeq = ColorHistEQ()
rgbsharpener = RGBSharpener()

def makepath(p):
    if not os.path.exists(p):
        os.mkdir(p)
    return p

def SaturationADJ(img, function, *arg):
    img_ = img.copy()
    # H,S,I
    img_[..., 1] = function(img[..., 1], *arg)
    return img_

def Batch_imgs_processing(imgs, apply_method, apply_domain, given_domain=rgb, *arg, **kwarg)->list:
    ret = []
    pbar = tqdm(imgs)
    for img in pbar:
        pbar.set_postfix_str(f"{img.name}")
        
        applyon = convertor.convert(
            img=img.img, fromD=given_domain, 
            toD=apply_domain
        )
        
        processed_img =  apply_method(applyon, *arg, **kwarg)
        
        processed_rgbimg = convertor.convert(
            img=processed_img, fromD=apply_domain, 
            toD=rgb
        )
        ret.append(rgbimg(img = processed_rgbimg, name=img.name))
    return ret

def sigmoid(x):
    return 1/(1+np.exp(-x))

if __name__ == "__main__":
    testimgsdir =os.path.join("HW3_test_image")
    imgs = readimgs(imgdir=testimgsdir)
    resultdir = makepath(os.path.join("result"))
    
    print("HistEQ on RGB")
    rgbhis= Batch_imgs_processing(
        imgs, histeq.transform, 
        rgb, rgb, 
        "global", rgb, 
    )
    saveimgs(
        imgs=rgbhis, 
        savepath=makepath(os.path.join(resultdir,"HistEQ_RGB"))
    )
    print("="*50)
    
    print("HistEQ on I of HSI")
    hsihis = Batch_imgs_processing(
        imgs, histeq.transform, 
        hsi, rgb, 
        "global", hsi 
    )
    saveimgs(
        imgs=hsihis, 
        savepath=makepath(os.path.join(resultdir,"HistEQ_I"))
    )
    print("="*50)

    print("HistEQ on S,I of HSI")
    hsihis_s = Batch_imgs_processing(
        imgs, histeq.transform, 
        hsi, rgb, 
        "global", hsi, required_channel=[1,2]
    )
    saveimgs(
        imgs=hsihis_s,
        savepath=makepath(os.path.join(resultdir,"HistEQ_SI"))
    )
    print("="*50)

    hsihis_sadj = Batch_imgs_processing(
        hsihis_s,SaturationADJ,hsi,rgb,
        sigmoid
    )
    saveimgs(
        imgs=hsihis_s,
        savepath=makepath(os.path.join(resultdir,"HistEQ_SI_sigS"))
    )
    print("="*50)

    print("Sharpening on RGB")
    sharpening = Batch_imgs_processing(
        imgs, rgbsharpener.Laplacian_Sharpening, 
        rgb, rgb, 
        False
    )
    saveimgs(
        imgs=sharpening, 
        savepath=makepath(os.path.join(resultdir,"RGBsharpening"))
    )
    print("="*50)
    
    print("Sharpening on RGB & Hist on I of HSI")
    hsihis_sharpen = Batch_imgs_processing(
        sharpening, histeq.transform, 
        hsi, rgb,
        "global", hsi
    )
    saveimgs(imgs=hsihis_sharpen, savepath=makepath(os.path.join(resultdir,"Hist_N_sharp")))
    print("="*50)
