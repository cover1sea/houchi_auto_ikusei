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
pre_ss = r"%s\pre_status.png" %(ss_dir)
ss = r"%s\status.png" %(ss_dir)
#tesseract(ocr)のディレクトリ
pyocr.tesseract.TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
tool = pyocr.get_available_tools()[0]

preStatusxy = [
        380, 500,        #y1, y2
        130, 194       #x1, x2
] 
statusxy = [
        380,500,
        360, 417
]

tapxy=[
        [150, 680],     #c級/cancel
        [380, 680]      #b級/accept
]

def tap(n):
    subprocess.call("nox_adb shell input touchscreen tap %d %d" % (tapxy[n][0], tapxy[n][1]), \
        shell=True, cwd=nox_dir)
    time.sleep(0.5)

def getStatus():
    subprocess.call("nox_adb exec-out screencap -p > screen_1.png", shell=True, cwd=ss_dir)
    img = cv2.imread(r"%s\screen_1.png" %(ss_dir))
    cv2.imwrite(pre_ss, 
                img[preStatusxy[0]:preStatusxy[1], preStatusxy[2]:preStatusxy[3]])
    cv2.imwrite(ss, 
                img[statusxy[0]:statusxy[1], statusxy[2]:statusxy[3]])

    # time.sleep(1)


def calcStatus(a,b,c,d):
    preParam = tool.image_to_string(
        Image.open(pre_ss),
        lang="eng",
        builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
    ).split()
    param = tool.image_to_string(
        Image.open(ss),
        lang="eng",
        builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
    ).split()

    if(len(param) != 4 | len(preParam) != 4):
        print("Cannot get status...")
        sys.exit()

    print("筋力(%.2f)：%d\n敏捷(%.2f)：%d\n知力(%.2f)：%d\n体力(%.2f)：%d" %(a,int(param[0]) - int(preParam[0]),
                b, int(param[1]) - int(preParam[1]),
                c, int(param[2]) - int(preParam[2]),
                d, int(param[3]) - int(preParam[3])))

    calc = (int(param[0]) - int(preParam[0])) * a \
                + (int(param[1]) - int(preParam[1])) * b \
                + (int(param[2]) - int(preParam[2])) * c \
                + (int(param[3]) - int(preParam[3])) * d \

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

    getStatus()
    param_zero = tool.image_to_string(
        Image.open(pre_ss),
        lang="eng",
        builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
    ).split()

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
    param_end = tool.image_to_string(
        Image.open(pre_ss),
        lang="eng",
        builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
    ).split()

    print("result:")
    print("筋力：{:+}、敏捷：{:+}、知力：{:+}、体力：{:+}". format(int(param_end[0]) - int(param_zero[0]),
                                                                int(param_end[1]) - int(param_zero[1]),
                                                                int(param_end[2]) - int(param_zero[2]),
                                                                int(param_end[3]) - int(param_zero[3])))

main(sys.argv)
