#----------------
# main.py
#----------------
#内容：  创建 摄像头cam, 预处理图像img_ori
#        操作 图像处理函数, 识别函数, 界面操作系统函数
#        
#----------------
#创建时间： 2025.3.6
#创建人：yst2219
#----------------


import os

from numpy import void
os.chdir(os.path.dirname(__file__))

from maix import app, time, display
#import numpy as np
#import cv2
from Img_Processing_1 import image_processing_1

def main():

    while not app.need_exit():

        time.fps_start()
        # img = img.lens_corr(strength=1.2)	# 调整strength的值直到画面不再畸变
        image_processing_1()
        # time.sleep(5)       #识别并输出后，停止进入image_processing函数5秒

if __name__ == "__main__":
    main()
    
