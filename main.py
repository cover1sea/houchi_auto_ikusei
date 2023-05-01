## $python main.py c|b 筋力 敏捷 知力 体力 育成回数 ##
import time
import datetime
import sys
import os
import subprocess
import signal
import random
import csv
#import cv2
import pyocr
import pyocr.builders
from PIL import Image, ImageChops
import numpy as np

#nox_adbのディレクトリ *不要なのでコメントアウト
#nox_dir = r"F:\\Nox\bin"
ss_dir = r"%s\tmp" %(os.getcwd())
pre_ss = r"%s\pre_status" %(ss_dir)
ss = r"%s\status" %(ss_dir)
data_log_path = r"%s\log" %(os.getcwd())

stopFilePath = r"%s\stop" %(os.getcwd())
#tesseract(ocr)のディレクトリ
pyocr.tesseract.TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
tool = pyocr.get_available_tools()[0]
builder=pyocr.builders.DigitBuilder(tesseract_layout=10)
builder.tesseract_configs.append("digits")
dev_addr = "0.0.0.0"

MAX_OCR_RETRY = 5
NUM_ARGS = 7
NUM_ARGS_DEV = 8
SEC_WAIT_TAP = 0.3
SEC_WAIT_GET_STATUS = 0
SEC_RETRY_GET_STATUS_INTERVAL = 1
SEC_RETRY_OCR_INTERVAL = 2.5
SEC_WAIT_SIGINT = 2
SEC_WAIT_KAKIN = 0.5 #+SEC_WAIT_TAP

calc_threshold=0 #育成計算値チェック

res_x=0
res_y=0
##540p point value
preStatusxy = [
    [388, 410,        #y1, y2
    141, 200],        #x1, x2
    [419, 440,
    141, 200],
    [448, 470,
    141, 200],
    [478, 502,
    141, 200]
] 
statusxy = [
    [388, 410,        #y1, y2
    352, 419],        #x1, x2
    [419, 440,
    352, 419],
    [448, 470,
    352, 419],
    [478, 502,
    352, 419]
]

# × の位置(色は255,255,255)
kakinxy = [496, 41]
#フレームでv2判断 v1:(201,182,137)くらい、v2:(49,38,29)くらい
clv2xy = [400, 1685]
tapxy=[
        [200, 700],     #c級/cancel
        [380, 680],     #b級/accept
        [496, 41],       #課金ポップアップ×
        [200, 800]      #a級
]

TAP_C     = 0
TAP_B     = 1
TAP_KAKIN = 2
TAP_A     = 3

param_zero = list()


def main(args):
    init(args)
    exec_ikusei(args)
    show_result()

def init(args):
    global dev_addr
    global data_log_path
    global calc_threshold
    now = datetime.datetime.now()
    data_log_path = data_log_path + "\\log_" + args[1] + now.strftime('_%Y%m%d_%H%M%S') + '.csv'

    signal.signal(signal.SIGINT, sigint_handler)
    if len(args)!=NUM_ARGS and len(args) != NUM_ARGS_DEV:
        print("err: number of args not matched.")
        print(args)
        exit()
    if len(args) == NUM_ARGS_DEV:
        dev_addr = args[7]
    else:
        dev_str = subprocess.check_output(["nox_adb", "devices"])
        dev_addr = dev_str.decode("utf-8").splitlines()[1].split("\t")[0]
    if not os.path.exists(ss_dir):
        print("err: ss_dir not exist")
        print(ss_dir)
        exit()
    resolution_adjustment()
    img = getStatus()
    for i in range(4):
        param_zero.append(
            tool.image_to_string(
                img.crop(([preStatusxy[i][2], preStatusxy[i][0], preStatusxy[i][3], preStatusxy[i][1]])),
                lang="eng",
                builder=builder
            ).replace(".", "")
        )
    calcStatus.preParam = list()
    for i in range(4):
        calcStatus.preParam.append(param_zero[i])
    if args[1] == 'c':
        calc_threshold = 15
    elif args[1] == 'b':
        calc_threshold = 18
    else:
        calc_threshold = 26

def sigint_handler(signal, frame):
    print("---script terminated by SIGINT---")
    time.sleep(SEC_WAIT_SIGINT)
    show_result()
    exit()

def exec_ikusei(args):
    print("---script start---")
    for i in range(int(args[6])):
        #stopファイル確認
        if os.path.isfile(stopFilePath):
            os.remove(stopFilePath)
            print("script stop by stop command")
            break

        print("%d/%d" %(i+1,int(args[6])))

        if args[1] == 'c':
                tap(TAP_C)
        elif args[1] == 'b':
                tap(TAP_B)
        elif args[1] == 'a':
                tap(TAP_A)
        else:
            print("err: 1つ目の引数が不正です")
            print(args)
            exit()
        calcStatus.ocr_failure_cnt = 0
        calcStatus(float(args[2]),float(args[3]),float(args[4]),float(args[5]))
        print("-----\n")

    print("---script end---")

def show_result():
    img = getStatus()
    param_end = list()
    for i in range(4):
        param_end.append(
            tool.image_to_string(
                img.crop(([preStatusxy[i][2], preStatusxy[i][0], preStatusxy[i][3], preStatusxy[i][1]])),
                lang="eng",
                builder=builder
            ).replace(".", "")
        )

    print("result:")
    print("筋力：{:+}、敏捷：{:+}、知力：{:+}、体力：{:+}". format(int(param_end[0]) - int(param_zero[0]),
                                                                int(param_end[1]) - int(param_zero[1]),
                                                                int(param_end[2]) - int(param_zero[2]),
                                                                int(param_end[3]) - int(param_zero[3])))

def resolution_adjustment():
    global preStatusxy, statusxy, res_x, res_y
    default_x = 540
    default_y = 960
    res = subprocess.run("nox_adb -s %s shell wm size" %(dev_addr), shell=True, stdout=subprocess.PIPE)
    resol = res.stdout
    if "540" in str(resol):
        print("540p")
        res_x = 540
        res_y = 960
        print(resol)
        print("warn: 解像度が低すぎるため誤認識率が高くなる可能性があります。(推奨：1080p)")
        return
    elif "720" in str(resol):
        print("720p")
        res_x = 720
        res_y = 1280
        print("warn: 解像度が低すぎるため誤認識率が高くなる可能性があります。(推奨：1080p)")
    elif "900" in str(resol):
        print("900p")
        res_x = 900
        res_y = 1600
    elif "1080" in str(resol):
        print("1080p")
        res_x = 1080
        res_y = 1920
    elif "1440" in str(resol):
        print("1440p")
        res_x = 1440
        res_y = 2560
    elif "2160" in str(resol):
        print("2160p")
        res_x = 2160
        res_y = 3840
    else :
        print("err: unexpected screen resolution")
        exit()
    print(resol)
    if isClientV2(res_x, res_y):
        print("Houchi client V.2-")

    else:
        print("Houchi client V.1")
        ##540p point value
        preStatusxy = [
                [380, 405,        #y1, y2
                135, 193],        #x1, x2
                [405, 435,
                135, 193],
                [435, 465,
                135, 193],
                [465, 495,
                135, 193]
        ] 
        statusxy = [
                [380, 405,        #y1, y2
                348, 416],        #x1, x2
                [405, 435,
                348, 416],
                [435, 465,
                348, 416],
                [465, 495,
                348, 416]
        ]
        
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
    for i in range(4):
        tapxy[i][0] = int(tapxy[i][0]*res_x/default_x)
        tapxy[i][1] = int(tapxy[i][1]*res_y/default_y)
    kakinxy[0] = int(kakinxy[0]*res_x/default_x)
    kakinxy[1] = int(kakinxy[1]*res_y/default_y)

def isClientV2(res_x, res_y):
    #V1廃止のため常にtrue
    return True
    
    #フレームでv2判断 v1:(201,182,137)くらい、v2:(49,38,29)くらい
    subprocess.call("nox_adb -s %s exec-out screencap -p > screen_1.png" % (dev_addr), shell=True, cwd=ss_dir)
    img = cv2.imread(r"%s\screen_1.png" %(ss_dir))
    if img[int(clv2xy[1]*res_y/1920)][int(clv2xy[0]*res_x/1080)][2] > 100 and img[int(clv2xy[1]*res_y/1920)][int(clv2xy[0]*res_x/1080)][1] > 100 :
        return False #v1
    else:
        return True #v2
    
def tap(n):
    subprocess.call("nox_adb -s %s shell input touchscreen tap %d %d" % (dev_addr, tapxy[n][0], tapxy[n][1]), \
        shell=True)
    time.sleep(SEC_WAIT_TAP)

def getStatus():
    #subprocess.call("nox_adb -s %s exec-out screencap -p > screen_1.png" % (dev_addr), shell=True, cwd=ss_dir)
    #img = cv2.imread(r"%s\screen_1.png" %(ss_dir))
    img = ImageSS_PIL()

    """育成中にポップアップ出なくなったようなのでいったんコメントアウト
    while isPopedKakinScreen(img):
        print("info: 課金ポップアップ検出")
        tap(TAP_KAKIN)
        time.sleep(SEC_WAIT_KAKIN)
        #subprocess.call("nox_adb -s %s exec-out screencap -p > screen_1.png" % (dev_addr), shell=True, cwd=ss_dir)
        #img = cv2.imread(r"%s\screen_1.png" %(ss_dir))
        img = ImageSS()
    """
    
    #time.sleep(SEC_WAIT_GET_STATUS)
    img_gray = img.convert("L")
    img_bin = img_gray.point(lambda _: 1 if _ > 180 else 0, mode="1")
    return img_bin

def isPopedKakinScreen(img):
    return img[kakinxy[1]][kakinxy[0]][0] == 255 and img[kakinxy[1]][kakinxy[0]][1] == 255 and img[kakinxy[1]][kakinxy[0]][2] == 255

def calcStatus(a,b,c,d):
    global calc_threshold
    rnd_width = 1.1 #画像の横幅拡大倍率、認識改善用
    img = getStatus()
    while(1):
        param = list()
        for i in range(4):
 
            img_d = img.crop(([statusxy[i][2], statusxy[i][0], statusxy[i][3], statusxy[i][1]]))
            img_resiz = img_d.resize((int(img_d.width * rnd_width), img_d.height))
            param.append(
                        tool.image_to_string(
                            img_resiz,
                            lang="eng",
                            builder=builder
                        ).replace(".", "")
            )
            
        #print(preParam)
        #print(param)
        try:
            calc = (float(param[0]) - float(calcStatus.preParam[0])) * a \
                        + (float(param[1]) - float(calcStatus.preParam[1])) * b \
                        + (float(param[2]) - float(calcStatus.preParam[2])) * c \
                        + (float(param[3]) - float(calcStatus.preParam[3])) * d
        except ValueError:
            calcStatus.ocr_failure_cnt += 1
            if calcStatus.ocr_failure_cnt > MAX_OCR_RETRY:
                print("warn: OCRリトライ回数超過、ステータスリセットのため育成確定します")
                tap(TAP_B)
                break
            print("warn: 育成ステータスが読み込めません...%d"  %(calcStatus.ocr_failure_cnt))
            print(param + calcStatus.preParam)
            img = ImageSS_PIL()
            img_rgb = np.array(img)[tapxy[0][1],tapxy[0][0], 0]
            time.sleep(SEC_RETRY_GET_STATUS_INTERVAL)
            if img_rgb > 150:
                img = getStatus()
                calcStatus.preParam = list()
                for i in range(4):
                    img_d = img.crop(([preStatusxy[i][2], preStatusxy[i][0], preStatusxy[i][3], preStatusxy[i][1]]))
                    img_resiz = img_d.resize((int(img_d.width * rnd_width), img_d.height))
                    calcStatus.preParam.append(
                        tool.image_to_string(
                            img_resiz,
                            lang="eng",
                            builder=builder
                        ).replace(".", "")
                    )
                continue
            else:
                return

        print("筋力(%.2f)：%d\t(%s -> %s)\n敏捷(%.2f)：%d\t(%s -> %s)\n知力(%.2f)：%d\t(%s -> %s)\n体力(%.2f)：%d\t(%s -> %s)" %(
                    a,int(param[0]) - int(calcStatus.preParam[0]), calcStatus.preParam[0], param[0],
                    b, int(param[1]) - int(calcStatus.preParam[1]), calcStatus.preParam[1], param[1],
                    c, int(param[2]) - int(calcStatus.preParam[2]), calcStatus.preParam[2], param[2],
                    d, int(param[3]) - int(calcStatus.preParam[3]), calcStatus.preParam[3], param[3]))

        #誤認識用
        flg_ocr_failure = 0
        for i in range(4):
            if abs(int(param[i]) - int(calcStatus.preParam[i])) > calc_threshold: #育成変動値はcalc_thresholdを超えない
                calcStatus.ocr_failure_cnt += 1
                if calcStatus.ocr_failure_cnt > MAX_OCR_RETRY:
                    print("warn: OCRリトライ回数超過、ステータスリセットのため育成確定します")
                    tap(TAP_B)
                    flg_ocr_failure = 2   
                else:
                    print("warn: OCR誤認識検知、ステータスを再読み込みします...%d" %(calcStatus.ocr_failure_cnt))
                    time.sleep(SEC_RETRY_OCR_INTERVAL)
                    flg_ocr_failure = 1
                img = getStatus()
                calcStatus.preParam = list()
                rnd_width = random.uniform(1,1.3)
                for i in range(4):
                    img_d = img.crop(([preStatusxy[i][2], preStatusxy[i][0], preStatusxy[i][3], preStatusxy[i][1]]))
                    img_resiz = img_d.resize((int(img_d.width * rnd_width), img_d.height))
                    calcStatus.preParam.append(
                        tool.image_to_string(
                            img_resiz,
                            lang="eng",
                            builder=builder
                        ).replace(".", "")
                    )
                break
        if flg_ocr_failure == 1:
            continue
        elif flg_ocr_failure == 2:
            break

        ## 誤認識がなければここまでくる
        print("Calculation Res: %.2f" %calc)
        str_yn = ""
        if calc > 0:
            print("Accept")
            tap(TAP_B)
            for i in range(4):
                calcStatus.preParam[i] = param[i]
            str_yn = "y"
        else:
            print("Cancel")
            tap(TAP_C)
            str_yn = "n"

        with open (data_log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["",calcStatus.preParam[0],calcStatus.preParam[1],calcStatus.preParam[2],calcStatus.preParam[3], str_yn])
        break

def ImageSS_PIL():
    pipe = subprocess.Popen("nox_adb -s %s exec-out screencap " % (dev_addr), stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    image_bytes = pipe.stdout.read()
    return Image.frombuffer("RGBA", (res_x, res_y), image_bytes, "raw", "RGBA", 0, 1)

if __name__ == '__main__':    
    main(sys.argv)