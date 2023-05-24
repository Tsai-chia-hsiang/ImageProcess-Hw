import os
from tqdm import tqdm
from ColorIMGkit.cimgcvtr import DomainConvertor as dcvtor
from ColorIMGkit.histEQ import ColorHistEQ
from ColorIMGkit.sharpening import RGBSharpener
from ColorIMGkit.RGBimgIO import readimgs, saveimgs, rgbimg

converter = dcvtor()
histeq = ColorHistEQ()
rgbsharpler = RGBSharpener()


def makepath(p):
    if not os.path.exists(p):
        os.mkdir(p)
    return p

def HistorgramEQ(imgs_ , domain):
    imgs = []
    print(f"Hist in {domain}")
    pbar = tqdm(imgs_)
    for img in pbar:
        pbar.set_postfix_str(f"{img.name}")
        d = converter.convert(img.img, fromD="rgb", toD = domain)
        d = histeq.transform(img=d,domain=domain)
        rgb = converter.convert(d, fromD = domain, toD="rgb")
        imgs.append(rgbimg(name=img.name, img=rgb))
    return imgs 

def RGBSharpening(imgs_, strong_mask=False):
    print(f"RGB sharpening")
    imgs = []
    pbar = tqdm(imgs_)
    for img in pbar:
        pbar.set_postfix_str(f"{img.name}")
        rgb = rgbsharpler.Laplacian_Sharpening(
            img.img,strong_mask=strong_mask
        )
        imgs.append(rgbimg(name=img.name, img=rgb))
    return imgs


if __name__ == "__main__":
    testimgsdir =os.path.join("HW3_test_image")
    imgs = readimgs(imgdir=testimgsdir)
    resultdir = makepath(os.path.join("result"))

    rgbhis= HistorgramEQ(imgs_=imgs, domain="rgb")
    saveimgs(imgs=rgbhis, savepath=makepath(os.path.join(resultdir,"RGB_directly_hist")))
    print("="*50)
    
    hsihis = HistorgramEQ(imgs_=imgs, domain="hsi")
    saveimgs(imgs=hsihis, savepath=makepath(os.path.join(resultdir,"HistEQ_HSI")))
    print("="*50)

    rgbsh = RGBSharpening(imgs_=imgs,strong_mask=False)
    saveimgs(imgs=rgbsh, savepath=makepath(os.path.join(resultdir,"RGBSharpening")))
    print("="*50)

    sharp_n_his = HistorgramEQ(imgs_= rgbsh, domain="hsi")
    saveimgs(imgs=sharp_n_his, savepath=makepath(os.path.join(resultdir,"sharp_n_hist")))
    print("="*50)
