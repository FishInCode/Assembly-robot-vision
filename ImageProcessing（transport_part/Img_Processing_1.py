#----------------
#图像处理_1: LAB通道调参 | 高斯、双边滤波 | 开操作一次 | Canny边缘检测（慢）| Cv2库的识别角点和逼近多边形

#Img_Precessing.py
#功能：传送带识别(包括形状识别、位置识别)
#----------------
#2025.3.6 ———2025.
#yst2219 
#----------------
#
# 
#------------------------------------------------------------问题：

from maix import image, display, time, nn, time, camera
import math

from UART import Uart      #请无视这个红线

cam = camera.Camera(200, 200)       #配置摄像头
cam.skip_frames(30)                 #跳过前三十帧
disp=display.Display()
detector1 = nn.YOLOv5(model="/root/models/maixhub/206852/model_206852.mud", dual_buff = True)       #矩形梯形专用
# detector2 = nn.YOLOv5(model="/root/models/maixhub/201139/model_201139.mud", dual_buff = True)

detector2 = nn.YOLOv5(model="/root/models/maixhub/207251/model_207251.mud", dual_buff = True)

thresholds_object1_On= [[56,83,-6,4,-4,7]]                 # 上机后的white阈值 圆形
thresholds_object2_On= [[45,74,-1,17,-12,10]]           # 上机white LAB正方形专用 注意：后两个值范围分别是(-129,-10),(10,127)   [[45,90,-4,17,-10,6]] 
thresholds_object3_On = [[28, 52, -22, 4, 0, 17]]       #位于第二阶段的三角取值
# thresholds_object3_On= [[66,100,-19,17,-10,2]]         # 上机后的white阈值 三角形 梯形(?)
# thresholds_object3_OnL= [[78,100,-19,17,-10,2]]         # 上机后的white阈值 三角形 梯形(?)
thresholds_object4_On= [[45,90,-4,17,-10,6]]            # 上机后的white阈值 梯形 注意：第三个值范围为(-4,0)后两个值分别取低取高无所谓

FFFlag = 0
distance_x = 0
rect_flag = 0
flag_1= 0
Flag_diuqi = 0

'''
颜色切换还是太复杂了，相比于每种颜色判断都切换对应的颜色参数，能不能直接通过改变图像格式只使用一个参数？
e.g.    仅使用识别红色参数,在识别蓝色时将图像格式从RGB切换为BGR
'''

#以下是识别圆的代码
def Circle_find(thresholds_color: list[list[int]], img: image.Image):
    
    # 图像坐标为：(a.x(),a.y()),直径为 a.r() ; 或 corners (内含所识别到的红色占据图中矩形的四点坐标)
    
    circles = img.find_circles(threshold = 4000,x_margin=20,y_margin=20,r_margin=20,r_min=45,r_max=65,r_step=5)   #rmin = 45
    #以下是识别 某种颜色圆 的代码
    color_blobs = img.find_blobs(thresholds_color, area_threshold = 100, pixels_threshold = 100)
    for b in color_blobs:
        # corners = b.corners()
        for a in circles:
            img.draw_circle(a.x(), a.y(), a.r(), image.COLOR_RED, 2)
            disp.show(img)
            return a

def Circle_cal(object:list, distance_x_dif:int):
    global FFFlag, distance_x
    while 1:        #要停得慢，识别得快，但是不能提前识别
        i = 0
        if FFFlag in range(0,51):       #50次
            FFFlag += 1
            if distance_x == distance_x_dif:
                i += 1
            if i>70:
                Uart(object[0],distance_x,b'\xFC')
                FFFlag = 0
                return 0
            distance_x = distance_x_dif
            continue
        elif FFFlag >50:           #FFFlag = 51或更大
            print(distance_x)
            # force = object[3]
            if distance_x > 125:
                distance_x = 125
            elif distance_x <0:
                distance_x = 0
                
            distance_x -= 18
            print (distance_x,"\t\t",object[0],"\t\t")
            Uart(object[0],distance_x,b'\xFC')
            FFFlag = 0
            return 0
        else:       #FFFlag = 0的时候
            continue

#以下是识别矩形的代码
def Rectangular_find(img: image.Image):         #色块识别不尽人意，先暂时转用Yolov5算法 #Yolov5就是个lj，无法区分正方形和梯形，还得是形状识别
    global rect_flag
    flag7 = 0
    img = img.lens_corr(strength=1.2)	# 调整strength的值直到画面不再畸变
    #以下是识别 白色颜色矩形 的代码     #用直线检测，根据交点个数区分梯形和正方形
    while 1:
        img = cam.read()

        rects = img.find_rects(threshold = 8000)       #roi = [24,24,149,154]
        print(rects)
        if rects!=[]:
            for a in rects:
                corners = a.corners()
                line1 = int(math.sqrt(math.pow((corners[0][0]-corners[1][0]),2)+math.pow((corners[0][1]-corners[1][1]),2)))
                line2 = int(math.sqrt(math.pow((corners[2][0]-corners[3][0]),2)+math.pow((corners[2][1]-corners[3][1]),2)))
                print(line1)
                print(line2)
                if (line1-line2) in range(-50,51):
                    rect = a.rect()
                    Rect = [rect[0]+(rect[2]/2),rect[1]+(rect[3]/3),rect[2],rect[3]]
                    return Rect
                else:
                    if rect_flag <3:
                        rect_flag +=1
                        continue
                    else:
                        break
        else:
            flag7 +=1
            if flag7 == 5:
                break
            continue

        

# def Trig_find(img: image.Image):
#     img_new = img.rotate(180)
#     objs = detector2.detect(img_new, conf_th = 0.2, iou_th = 0.2)
#     for obj in objs:
#         if obj.class_id == 3 :
#             print('1')
#             center_x = obj.x+(obj.w/2)
#             center_y = obj.y+(obj.h/2)
#             print(distance_x,'\t\t')
#             # if distance_x in range(70,130):
#             Trig = [center_x, center_y, obj.w, obj.h]

#             return Trig


def Trapz_find(img):
    objs = detector1.detect(img, conf_th = 0.5, iou_th = 0.5)

    for obj in objs:
        if obj.class_id == 3:
            center_x = obj.x+(obj.w/2)
            center_y = obj.y+(obj.h/2)

            Trapz = [center_x ,center_y ,obj.w ,obj.h ]

            return Trapz


def image_processing_1():
    global flag_1, Flag_diuqi
    while 1:
        time.fps_start()          # Manually set fps calculation start point, comment here mean last time fps() call is start
                                # | 动设置帧率（FPS）计算开始点，这里注释了表示上一次 fps 函数即是开始
        
        img = cam.read()
        img_new = img.affine([20,20,180,20,20,180],[0,0,200,0,0,200],200,200)
        circle = Circle_find(thresholds_object1_On, img)
        disp.show(img_new)
        # trig = Trig_find(img_new)
        # rectangular = Rectangular_find(img)
        trapz = Trapz_find(img_new)
        if circle == None and trapz == None :
            continue
        elif circle != None:        #圆的放置问题出在圆盘测左右移动上（偏右）
            object = [b'\x0A',3,[circle.x(),circle.y(),circle.r()],b'\x4F']   #格式为[形状，参数数量，参数列表，力度]
            circle = None
            ratio = 22.5 / object[2][2]     # 1mm/pixle 
            distance_x_dif = 67 + int((100 - object[2][0]) * ratio * (134/99))-10  #要求物块在视野内从左到右，否则该值取相反数
            print(distance_x_dif)
            if distance_x_dif in range(63,75):  #判中
                Uart(b'\x00',67,b'\x00')    #停传送带
                distance_x = distance_x_dif
                # if distance_x_dif in range(4,20):
                # flag_1= 0
                Circle_cal( object, distance_x_dif)
                break
            else:
                continue
        # elif trig != None:      #三角仅放置一次，需要更多读数（传送带45%）
        #     object = [b'\x0C',4,trig,b'\x51']
        #     # Uart(b'\x00',67,b'\x00')
        #     # print('2')
        #     trig = None
        #     ratio1 = 45 / object[2][2]
        #     ratio2 = 45 / object[2][3]
        #     ratio = (ratio1 + ratio2) / 2
        #     center = [object[2][0], object[2][1]]

            # distance_x = int((100 - center[0]) * ratio)
            # flag_1= 0
            # print(distance_x)
            # if distance_x in range(-45,-22):
            # distance_x = 67 - int((100 - center[0]) * ratio * (134/99)) -6 #减1或加1都会导致偏向喻，但是数值为9时便会夹取正中间（虽然放置时会偏喻
            # print(int((100 - center[0]) * ratio * (134/99)))
            # if distance_x in range(63,90):  #判中
            #     if distance_x > 125:
            #         distance_x = 125
            #     elif distance_x <0:
            #         distance_x = 0
            #     if Flag_diuqi  == 0:
            #         Flag_diuqi += 1
            #     elif Flag_diuqi<= 3:
            #         Flag_diuqi +=1

            #         print (distance_x,"\t\t",object[0],"\t\t")

            #         Uart(object[0],distance_x,b'\xFC')
            #         break

        elif trapz != None:                 #梯形正方形防止问题仍然有误识别和左右移动问题（偏右一点点，梯形未知）
            object = [b'\x0D',4,trapz,b'\x4F']      #格式为[形状，参数数量，参数列表，力度] #梯形 [  ,  ,[ x, y, w, h],  ]
            trapz = None
            # print('2')
            if flag_1 < 3:
                flag_1 += 1
                Uart(b'\x00',67,b'\x00')
                # time.sleep_ms(500)
                continue
            else:
                rect = Rectangular_find(img)       #再探再报
                if rect != None:                    #应是正方形
                    ratio = 45 / rect[2]
                    distance_x = 67 - int((100 - rect[0]) * ratio * (134/99)) -15
                    # print(distance_x)
                    if distance_x > 130:
                        distance_x = 130
                    elif distance_x <0:
                        distance_x = 0
                    print ("\t\t",distance_x,"\t\t",b'\x0B',"\t\t")
                    Uart(b'\x0B',distance_x,b'\xFC')
                    flag_1 = 0
                    Flag_diuqi = 0
                    break
                elif rect == None:                               #应是梯形
                    ratio1 = 45 / object[2][2]
                    ratio2 = 45 / object[2][3]
                    ratio = (ratio1 + ratio2) / 2
                    center = [object[2][0], object[2][1]]

                    # distance_x = int((100 - center[0]) * ratio)
                    # if distance_x in range(-20,20):
                    distance_x = 67 - int((100 - center[0]) * ratio * (134/99)) -15
                    # print(distance_x)
                    # distance_y = int((100 - center[1]) * ratio)
                    # force = object[3]
                    if distance_x > 130:
                        distance_x = 130
                    elif distance_x <0:
                        distance_x = 0
                    # print (distance_x,"\t\t",object[0],"\t\t") 
                    # if Flag_diuqi < 2:     #再再探再再报
                    #     Flag_diuqi += 1
                    #     continue
                    # else: 
                    print ("\t\t",distance_x,"\t\t",object[0],"\t\t")
                    Uart(object[0],distance_x,b'\xFC')
                    flag_1 = 0
                    Flag_diuqi = 0
                    break

            # return object

'''
# 以下是识别三角形和梯形（近似为四边形）的代码
def TrigATrapz_find(img: image.Image):
    import cv2
    import numpy as np
    kernel = np.ones((3,3), np.uint8)        #创建核
    # i =0

    img_raw = image.image2cv(img,ensure_bgr=False,copy=False)
    img_ = cv2.cvtColor(img_raw,cv2.COLOR_RGB2LAB)   #RGB转LAB
    #LAB_thresholds = [[0,71,-4,77,36,79]]    #原为红值，现为蓝值且后四项两组反转
    #LAB_thresholds = [[0,61,-128,127,-128,-30]]     #原为蓝值，现为红值

    # 解析LAB阈值参数（OpenCV的LAB范围特性是：L(0~255)；A(-128~127);B(-128~127)）
    Lmin,Lmax,Amin,Amax,Bmin,Bmax = LAB_thresholds[0]   #创建LAB通道的高低

    lower_bound = np.array([Lmin*255/100, Amin+128, Bmin+128])  #上下界限
    upper_bound = np.array([Lmax*255/100, Amax+128, Bmax+128])
    
    mask = cv2.inRange(img_, lower_bound, upper_bound)
        #第一个参数：src指的是原图
        #第二个参数：lower_red指的是图像中低于这个lower_red的值，图像值变为0
        #第三个参数：upper_red指的是图像中高于这个upper_red的值，图像值变为0
        #而在lower_red～upper_red之间的值变成255

    # if LAB_thresholds[0][3] <= 70:                               #绿色时掩图就取反
    #     mask = cv2.bitwise_not(mask)

    #img_raw = cv2.bitwise_and(img_raw,img_raw,mask=mask)        #颜色已抓取

    img_= cv2.GaussianBlur(mask,(5,5),0)     #高斯滤波
    img_= cv2.bilateralFilter(img_, 9, 75, 75) #双边滤波(去噪点)
    
    _, thresh = cv2.threshold(img_, 127, 255, cv2.THRESH_BINARY) #二值化
    #thresh = cv2.morphologyEx(img_raw, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(img_, cv2.MORPH_CLOSE, kernel) #闭运算(去噪点)  
    edged = cv2.Canny (thresh, 200, 600, L2gradient = True)    #Canny找边缘
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
    if len(contours) > 0:
        #筛选出最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
    
        epsilon =0.02 * cv2.arcLength(largest_contour,True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True) #approxPolyDP逼近多边形   approx格式为:[[[x1 y1]] [[x2 y2]] [[x3 y3]]]
        # if len(approx) > 10:  #如果角点数>=3
        #     print("这是圆")
        #     cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)
        if len(approx) == 3:
            # rect = cv2.minAreaRect(approx)  #获取最小外接矩形
            # points = cv2.boxPoints(rect)     #最小外接矩形的四点(顺序：右下；左下；右上；左上)
            # # center = rect[0]            
            # print(points)
            # cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)   #drawContours画出轮廓
            # for point in approx:
                # x, y = point.ravel()    #获取每个多边形角点坐标
                # cv2.circle(img=img_raw,center=(x,y),radius=5,color=(255,0,0),thickness=2) #circle画出多边形角点
            approx = approx.tolist()                                                  #approx从array转list，防止下面判断报错
            return approx                                                             #不测试的话就把point循环给删了，直接输出approx
                
        elif len(approx) == 4 :
            #cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)   #drawContours画出轮廓
            # for point in approx:
                # x, y = point.ravel()    #获取每个多边形角点坐标
                # cv2.circle(img=img_raw,center=(x,y),radius=5,color=(255,0,0),thickness=2) #circle画出多边形角点
            approx = approx.tolist()
            return approx
'''

