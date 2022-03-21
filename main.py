## $python main.py c|b 筋力 敏捷 知力 体力 育成回数 ##
import time
import sys
import os
import subprocess
import signal
import cv2
import pyocr
import pyocr.builders
from PIL import Image


#nox_adbのディレクトリ *不要なのでコメントアウト
#nox_dir = r"F:\\Nox\bin"
ss_dir = r"%s\tmp" %(os.getcwd())
pre_ss = r"%s\pre_status" %(ss_dir)
ss = r"%s\status" %(ss_dir)
#tesseract(ocr)のディレクトリ
pyocr.tesseract.TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
tool = pyocr.get_available_tools()[0]
builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
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
        348, 416],        #x1, x2
        [405, 435,
        348, 416],
        [435, 465,
        348, 416],
        [465, 495,
        348, 416]
]

tapxy=[
        [200, 700],     #c級/cancel
        [380, 680]      #b級/accept
]
param_zero = list()


def main(args):
    init(args)
    exec_ikusei(args)
    show_result()

def init(args):
    global dev_addr
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
    getStatus()
    for i in range(4):
        param_zero.append(
            tool.image_to_string(
                Image.open(pre_ss+str(i)+".png"),
                lang="eng",
                builder=builder
            ).replace(".", "")
        )
    calcStatus.preParam = list()
    for i in range(4):
        calcStatus.preParam.append(param_zero[i])

def sigint_handler(signal, frame):
    print("---script terminated by SIGINT---")
    time.sleep(SEC_WAIT_SIGINT)
    show_result()
    exit()

def exec_ikusei(args):
    print("---script start---")
    for i in range(int(args[6])):
        print("%d/%d" %(i+1,int(args[6])))

        if(args[1] == 'c'):
                tap(0)
        else:
                tap(1)
        
        calcStatus.ocr_failure_cnt = 0
        getStatus()

        calcStatus(float(args[2]),float(args[3]),float(args[4]),float(args[5]))
        print("-----\n")
    print("---script end---")
    
def show_result():
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

def resolution_adjustment():
    default_x = 540
    default_y = 960
    res = subprocess.run("nox_adb -s %s shell wm size" %(dev_addr), shell=True, stdout=subprocess.PIPE)
    resol = res.stdout
    if("540" in str(resol)):
        print("540p")
        #res_x = 540
        #res_y = 960
        print(resol)
        print("warn: 解像度が低すぎるため誤認識率が高くなる可能性があります。(推奨：1080p)")
        return
    elif("720" in str(resol)):
        print("720p")
        res_x = 720
        res_y = 1280
        print("warn: 解像度が低すぎるため誤認識率が高くなる可能性があります。(推奨：1080p)")
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
    tapxy[0][0] = int(tapxy[0][0]*res_x/default_x)
    tapxy[0][1] = int(tapxy[0][1]*res_y/default_y)
    tapxy[1][0] = int(tapxy[1][0]*res_x/default_x)
    tapxy[1][1] = int(tapxy[1][1]*res_y/default_y)


def tap(n):
    subprocess.call("nox_adb -s %s shell input touchscreen tap %d %d" % (dev_addr, tapxy[n][0], tapxy[n][1]), \
        shell=True)
    time.sleep(SEC_WAIT_TAP)

def getStatus():
    subprocess.call("nox_adb -s %s exec-out screencap -p > screen_1.png" % (dev_addr), shell=True, cwd=ss_dir)
    img = cv2.imread(r"%s\screen_1.png" %(ss_dir))
    ret, img_gray = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 160, 255, cv2.THRESH_BINARY)
    #ret, img_gray = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    for i in range(4):
        cv2.imwrite(pre_ss+str(i)+".png", 
                    img_gray[preStatusxy[i][0]:preStatusxy[i][1], preStatusxy[i][2]:preStatusxy[i][3]])
        cv2.imwrite(ss+str(i)+".png", 
                    img_gray[statusxy[i][0]:statusxy[i][1], statusxy[i][2]:statusxy[i][3]])

    time.sleep(SEC_WAIT_GET_STATUS)


def calcStatus(a,b,c,d):
    while(1):
        param = list()
        for i in range(4):
            """
            preParam.append(
                tool.image_to_string(
                    Image.open(pre_ss+str(i)+".png"),
                    lang="eng",
                    builder=builder
                ).replace(".", "")
            )
            """
            param.append(
                tool.image_to_string(
                Image.open(ss+str(i)+".png"),
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
            print("warn: 育成ステータスが読み込めません")
            img = cv2.imread(r"%s\screen_1.png" %(ss_dir))
            img_bgr = img[tapxy[0][1], tapxy[0][0], 2]
            time.sleep(SEC_RETRY_GET_STATUS_INTERVAL)
            if img_bgr > 150:
                getStatus()
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
            if abs(int(param[i]) - int(calcStatus.preParam[i])) > 20: #C級、B級の育成変動値は20を超えない
                calcStatus.ocr_failure_cnt += 1
                if calcStatus.ocr_failure_cnt > MAX_OCR_RETRY:
                    print("warn: OCRリトライ回数超過、ステータスリセットのため育成確定します")
                    tap(1)
                    flg_ocr_failure = 2   
                else:
                    print("warn: OCR誤認識検知、ステータスを再読み込みします...%d" %(calcStatus.ocr_failure_cnt))
                    time.sleep(SEC_RETRY_OCR_INTERVAL)
                    flg_ocr_failure = 1
                getStatus()
                calcStatus.preParam = list()
                for i in range(4):
                    calcStatus.preParam.append(
                        tool.image_to_string(
                            Image.open(pre_ss+str(i)+".png"),
                            lang="eng",
                            builder=builder
                        ).replace(".", "")
                    )
                break
        if flg_ocr_failure == 1:
            continue
        elif flg_ocr_failure == 2:
            break


        print("Calculation Res: %.2f" %calc)
        if (calc > 0):
            print("Accept")
            tap(1)
            for i in range(4):
                calcStatus.preParam[i] = param[i]

        else:
            print("Cancel")
            tap(0)
        break

if __name__ == '__main__':    
    main(sys.argv)