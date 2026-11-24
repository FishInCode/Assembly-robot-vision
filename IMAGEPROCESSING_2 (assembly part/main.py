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

os.chdir(os.path.dirname(__file__))

from cv2 import SUBDIV2D_NEXT_AROUND_LEFT
from maix import  app, time
#import numpy as np
#import cv2

# from Grab_Claw_init import cross_recog
import UART      #请无视这个红线
from UART import SUBF
# from Img_Processing_2 import image_processing_2
# from Img_Processing_2 import rotary_control_1, rotary_lib
from Img_Processing_3 import image_processing_3 
# from Img_Processing_3_shapematchmode1 import image_processing_3 

# flag = 0
color = None

# cam = camera.Camera(200, 200)       #配置摄像头
# cam.skip_frames(30)                 #跳过前三十帧




def main():
    global SUBF
    global color
    # global rotary_lib
    # global flag
    while not app.need_exit():
        # flag_2 = 0
        # time.fps_start()
        # img = cam.read()

        # ao_count = 0
        SUBF = UART.received(UART.serial0)
        time.sleep_ms(1) # sleep to make CPU free
        # print(SUBF)

        # for i in range(0,8):
        #     ao = rotary_lib[i][1]
        #     if ao:
        #         ao_count +=1

        # if ao_count == 8:
        #     if flag == 0:
        #         flag = 1
        #         continue
        #     else:
        #         UART.Uart(8,0)      #示意单片机进入 只抓不塞 模式
        #         break
        image_processing_3('0x0a','0x01')
        # if SUBF != None:                #决赛代码（如果还有决赛的话）
        #     if SUBF[0] == '0x01':
        #         print("red")
        #         color = SUBF[0]
        #         print(color)
        #         SUBF = None
        #         continue
        #     elif SUBF[0] == '0x02':
        #         print("blue")
        #         color = SUBF[0]
        #         print(color)
        #         SUBF = None
        #         continue
        #     else:
        #         print("start")
        #         print(color)
        #         time.sleep_ms(300)
        #         image_processing_3(SUBF[0],color)
                # fps = time.fps()            # Calculate FPS between last time fps() call and this time call.
                                        # | 计算两次 fps 函数调用之间的帧率
                # print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}") # print FPS in console
                                                        # | 在终端打印帧率（FPS）
















        

        # image_processing_2('0x0c',128)
        # image_processing_3('0x0c',128)
        # fps = time.fps()            # Calculate FPS between last time fps() call and this time call.
        #                         # | 计算两次 fps 函数调用之间的帧率
        # print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}") # print FPS in console
        #                                             # | 在终端打印帧率（FPS）

        

        # fps = time.fps()                # Calculate FPS between last time fps() call and this time call.
        #                             # | 计算两次 fps 函数调用之间的帧率
        # print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")  #在终端打印帧率 (FPS)

        # if object == None:
        #     continue
        # elif object[0] == b'\x01':         #圆形
        #     if flag_2 ==0:
        #         flag_2 += 1
        #         continue
        #     else:
        #         flag_2 = 0
        #         ratio = object[2][2] / 225     # pixel / 0.1mm 
        #         distance_x = int((100 - object[2][0]) * ratio) + 730    #要求物块在视野内从左到右，否则该值取相反数
        #         distance_y = int((100 - object[2][1]) * ratio)
        #         # Info_Processing( distance_x, distance_y)
        #         print (distance_x,"\t\t",distance_y,"\t\t")
        #         # time.sleep_ms(1000)
        #         UART.Uart(distance_x,distance_y)
            
        # elif object[0] == b'\x02':         #正方形
        #     if flag_2 ==0:
        #         flag_2 += 1
        #         continue
        #     else:
        #         flag_2 = 0
        #         ratio = object[2][2] / 225
        #         ratio += object[2][3] /225
        #         ratio = ratio / 2
        #         distance_x = int((100 - object[2][0] - 0.5*object[2][2]) * ratio) + 730
        #         distance_y = int((100 - object[2][1] - 0.5*object[2][3]) * ratio)

        #         UART.Uart(distance_x,distance_y)
        
        # elif object[0] ==b'\x03':          #三角形 [[a,b],[],[],[]]
        #     if flag_2 ==0:
        #         flag_2 += 1
        #         continue
        #     else:
        #         flag_2 = 0
        #         x1 = object[2][0][0]
        #         x2 = object[2][1][0]
        #         x3 = object[2][2][0]
        #         y1 = object[2][0][1]
        #         y2 = object[2][1][1]
        #         y3 = object[2][2][1]
        #         center = [int(x1/3+x2/3+x3/3), int(y1/3+y2/3+y3/3)]
        #         ratio = (((x1-x2) ** 2+(y1-y2) ** 2) ** 0.5) / 450 
        #         distance_x = int((100 - center[0]) * ratio) + 730
        #         distance_y = int((100 - center[1]) * ratio)

        #         UART.Uart(distance_x,distance_y)
            
        # elif object[0] ==b'\x04':          #梯形
        #     if flag_2 ==0:
        #         flag_2 += 1
        #         continue
        #     else:
        #         flag_2 = 0
        #         x1 = object[2][0][0]
        #         x2 = object[2][1][0]
        #         x3 = object[2][2][0]
        #         x4 = object[2][3][0]
        #         y1 = object[2][0][1]
        #         y2 = object[2][1][1]
        #         y3 = object[2][2][1]
        #         y4 = object[2][3][1]
        #         center = [int(x1/4+x2/4+x3/4+x4/4),int(y1/4+y2/4+y3/4+y4/4)]
        #         ratio = (((x1-center[0]) ** 2+(y1-center[1]) ** 2) ** 0.5) / 270    #270mm 为梯形角点到重心的距离
        #         distance_x = int((100 - center[0]) * ratio) + 730
        #         distance_y = int((100 - center[1]) * ratio)

        #         UART.Uart(distance_x,distance_y)
      


if __name__ == "__main__":
    main()
    
