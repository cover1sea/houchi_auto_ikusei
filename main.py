## $python main.py c|b 筋力 敏捷 知力 体力 育成回数 ##
import time
import sys
import os
import subprocess
import cv2
import pyocr
import pyocr.builders
from PIL import Image


#nox_adbのディレクトリ
nox_dir = r"F:\\Nox\bin"
ss_dir = r"%s\tmp" %(os.getcwd())
pre_ss = r"%s\pre_status" %(ss_dir)
ss = r"%s\status" %(ss_dir)
#tesseract(ocr)のディレクトリ
pyocr.tesseract.TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
tool = pyocr.get_available_tools()[0]
builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
builder.tesseract_configs.append("digits")

##540p point value
preStatusxy = [
        [380, 405,        #y1, y2
        130, 193],        #x1, x2
        [405, 435,
        130, 193],
        [435, 465,
        130, 193],
        [465, 495,
        130, 193]
] 
statusxy = [
        [380, 405,        #y1, y2
        345, 416],        #x1, x2
        [405, 435,
        345, 416],
        [435, 465,
        345, 416],
        [465, 495,
        345, 416]
]

tapxy=[
        [150, 680],     #c級/cancel
        [380, 680]      #b級/accept
]



def resolution_adjustment():
    default_x = 540
    default_y = 960
    res = subprocess.run("adb shell wm size", shell=True, stdout=subprocess.PIPE, cwd=nox_dir)
    resol = res.stdout
    if("540" in str(resol)):
        print("540p")
        #res_x = 540
        #res_y = 960
        print(resol)
        return
    elif("720" in str(resol)):
        print("720p")
        res_x = 720
        res_y = 1280
    elif("900" in str(resol)):
        print("900p")
        res_x = 900
        res_y = 1600
    elif("1080" in str(resol)):
        print("1080p")
        res_x = 1080
        res_y = 1920
    elif("1440" in str(resol)):
        print("1440p")
        res_x = 1440
        res_y = 2560
    elif("2160" in str(resol)):
        print("2160p")
        res_x = 2160
        res_y = 3840
    else :
        print("err: unexpected screen resolution")
        exit()
    print(resol)
    ##ajust resolution
    for i in range(4):
        preStatusxy[i][0] = int(preStatusxy[i][0]*res_y/default_y)
        preStatusxy[i][1] = int(preStatusxy[i][1]*res_y/default_y)
        preStatusxy[i][2] = int(preStatusxy[i][2]*res_x/default_x)
        preStatusxy[i][3] = int(preStatusxy[i][3]*res_x/default_x)
        statusxy[i][0] = int(statusxy[i][0]*res_y/default_y)
        statusxy[i][1] = int(statusxy[i][1]*res_y/default_y)
        statusxy[i][2] = int(statusxy[i][2]*res_x/default_x)
        statusxy[i][3] = int(statusxy[i][3]*res_x/default_x)
    tapxy[0][0] = tapxy[0][0]*res_x/default_x
    tapxy[0][1] = tapxy[0][1]*res_y/default_y
    tapxy[1][0] = tapxy[1][0]*res_x/default_x
    tapxy[1][1] = tapxy[1][1]*res_y/default_y


def tap(n):
    subprocess.call("nox_adb shell input touchscreen tap %d %d" % (tapxy[n][0], tapxy[n][1]), \
        shell=True, cwd=nox_dir)
    time.sleep(0.5)

def getStatus():
    subprocess.call("nox_adb exec-out screencap -p > screen_1.png", shell=True, cwd=ss_dir)
    img = cv2.imread(r"%s\screen_1.png" %(ss_dir))
    ret, img_gray = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 160, 255, cv2.THRESH_BINARY)
    #ret, img_gray = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    for i in range(4):
        cv2.imwrite(pre_ss+str(i)+".png", 
                    img_gray[preStatusxy[i][0]:preStatusxy[i][1], preStatusxy[i][2]:preStatusxy[i][3]])
        cv2.imwrite(ss+str(i)+".png", 
                    img_gray[statusxy[i][0]:statusxy[i][1], statusxy[i][2]:statusxy[i][3]])

    #time.sleep(1)


def calcStatus(a,b,c,d):
    preParam = list()
    param = list()
    for i in range(4):
        preParam.append(
            tool.image_to_string(
                Image.open(pre_ss+str(i)+".png"),
                lang="eng",
                builder=builder
            ).replace(".", "")
        )
        param.append(
            tool.image_to_string(
            Image.open(ss+str(i)+".png"),
            lang="eng",
            builder=builder
            ).replace(".", "")
        )
    #print(preParam)
    #print(param)
    calc = (float(param[0]) - float(preParam[0])) * a \
                + (float(param[1]) - float(preParam[1])) * b \
                + (float(param[2]) - float(preParam[2])) * c \
                + (float(param[3]) - float(preParam[3])) * d
    """        for debug
    while calc>1000 or calc<-1000:
        print("debug %s:%s" %(preParam[3], param[3]))
        getStatus()
        preParam = list()
        param = list()
        for i in range(4):
            preParam.append(
                tool.image_to_string(
                    Image.open(pre_ss+str(i)+".png"),
                    lang="eng",
                    builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
                ).replace(".", "")
            )
            param.append(
                tool.image_to_string(
                Image.open(ss+str(i)+".png"),
                lang="eng",
                builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
                ).replace(".", "")
            )
        print(preParam)
        print(param)
        calc = (int(param[0]) - int(preParam[0])) * a \
                + (int(param[1]) - int(preParam[1])) * b \
                + (int(param[2]) - int(preParam[2])) * c \
                + (int(param[3]) - int(preParam[3])) * d
    """
    print("筋力(%.2f)：%d\n敏捷(%.2f)：%d\n知力(%.2f)：%d\n体力(%.2f)：%d" %(a,int(param[0]) - int(preParam[0]),
                b, int(param[1]) - int(preParam[1]),
                c, int(param[2]) - int(preParam[2]),
                d, int(param[3]) - int(preParam[3])))

    print("Calculation Res: %.2f" %calc)
    if (calc > 0):
        print("Accept")
        tap(1)

        time.sleep(2.5)

    else:
        print("Cancel")
        tap(0)

def main(args):
    print("---script start---")

    resolution_adjustment()
    getStatus()
    param_zero = list()
    for i in range(4):
        param_zero.append(
            tool.image_to_string(
                Image.open(pre_ss+str(i)+".png"),
                lang="eng",
                builder=builder
            ).replace(".", "")
        )

    for i in range(int(args[6])):
        print("%d/%d" %(i+1,int(args[6])))

        if(args[1] == 'c'):
                tap(0)
        else:
                tap(1)
        getStatus()

        calcStatus(float(args[2]),float(args[3]),float(args[4]),float(args[5]))
        print("-----\n")
    print("---script end---")
    getStatus()
    param_end = list()
    for i in range(4):
        param_end.append(
            tool.image_to_string(
                Image.open(pre_ss+str(i)+".png"),
                lang="eng",
                builder=builder
            ).replace(".", "")
        )

    print("result:")
    print("筋力：{:+}、敏捷：{:+}、知力：{:+}、体力：{:+}". format(int(param_end[0]) - int(param_zero[0]),
                                                                int(param_end[1]) - int(param_zero[1]),
                                                                int(param_end[2]) - int(param_zero[2]),
                                                                int(param_end[3]) - int(param_zero[3])))

main(sys.argv)
