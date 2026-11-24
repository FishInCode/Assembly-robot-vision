#----------------
#图像处理: LAB通道调参 | 高斯、双边滤波 | 开操作一次 | Canny边缘检测（慢）| Cv2库的识别角点和逼近多边形
#Img_Precessing_2.py
#功能：预赛第二部分图形识别（包括形状识别、颜色识别、位置识别）
#----------------
#2025.3.6 ———2025.
#yst2219 
#----------------
#
# 
#------------------------------------------------------------问题：图像红蓝颠倒

from maix import camera, image, display, time, nn
from UART import Uart
   
disp=display.Display() 

COUNT = 0       # COUNT是超级全局变量
rotary_lib = {0:[("blue",'0x0a'),0],1:[("red" ,'0x0d'),0],2:[("red" ,'0x0c'),0],3:[("blue",'0x0b'),0],   #结构：key:[("图形"，图形代号)，占用flag]
              4:[("red" ,'0x0a'),0],5:[("blue",'0x0d'),0],6:[("blue",'0x0c'),0],7:[("red" ,'0x0b'),0]}

cam = camera.Camera(200, 200)       #配置摄像头
cam.skip_frames(30)                 #跳过前三十帧
detector = nn.YOLOv5(model="/root/models/maixhub/205925/model_205925.mud", dual_buff = True)

thresholds_red = [[0, 75, 24, 79, -4, 77]]     #red LABx    [[0,71,36,79,-4,77]]          [[0, 75, 24, 79, -4, 77]]
thresholds_blue = [[0, 29, 0, 127, -128, -7]]    #blue LAB [[0,61,-128,127,-128,-30]]       [[0, 29, 0, 127, -128, -7]]
thresholds_object3_On = [[28, 52, -22, 4, 0, 17]]       #位于第二阶段的三角取值
# thresholds_redAblue = [[0,38,5,127,-128,127]]       #[(0, 34, 12, 127, -39, 18)]
# thresholds_green = [[0,70,-128,65,-128,33]]      #green LAB
# thresholds_object1= [[61,83,-6,4,-4,7]]              # white LAB适用于圆、三角形、梯形
thresholds_object2= [[56,69,-3,10,-1,10]]                             # white LAB正方形专用 #[[56,69,-3,10,-1,10]]
#识别传送带物块  68,-02,02rect 71,-03,00circle
#thresholds_green = [[21,41,-34,-14,-5,15]]     #green LAB#识别履带(自动采的也不知道好不好)


def rotary_control_1(massage):              # massage 是单片机(?) 传过来的物块信息，与第一阶段发送格式相同
    global COUNT
    global rotary_lib   #rotary_lib = {0:[("blue",'\x0A'),0],1:[("red" ,'\x0B'),0],2:[("blue",'\x0C'),0],3:[("blue",'\x0D'),0],   #结构：key:[("图形"，图形代号)，是否已用flag]
                        #              4:[("red" ,'\x0A'),0],5:[("blue",'\x0B'),0],6:[("red" ,'\x0C'),0],7:[("red" ,'\x0D'),0]}
    pos_dif = 0
    # print(massage)
    while 1:
        COUNT %=8
        if massage == None:
            # COUNT = 0
            break
        elif (massage[0] == rotary_lib[COUNT][0][1]) and (rotary_lib[COUNT][1] == 0):
            Uart(pos_dif,0)
            # print(pos_dif)
            rotary_lib[COUNT][1] = 1
            pos_dif = 0
            # COUNT = 0
            break
        else :
            COUNT +=1
            pos_dif += 1    #可能此处算法会让转盘多转一个45度，若会就在Uart(pos_dif,0)前将pos_dif减1

    return 0
    
'''
颜色切换还是太复杂了，相比于每种颜色判断都切换对应的颜色参数，能不能直接通过改变图像格式只使用一个参数？
e.g.    仅使用识别红色参数,在识别蓝色时将图像格式从RGB切换为BGR
'''

def image_processing_2(shape:str, color):
    # disp.show(img)
    while 1:
        img = cam.read()

        # print(shape)
        if  color == b'\x02':     #蓝值
            img = img.binary(thresholds_blue)
            img = img.rotate(275)
        elif color == b'\x01':  #红值
            img = img.binary(thresholds_red)
            img = img.rotate(275)
        elif color == b'\x03':  #红蓝两色
            img1 = img.binary(thresholds_blue,copy = True)
            img2 = img.binary(thresholds_red, copy = True)
            img = img1.b_or(img2)
            img = img.rotate(275)
        # disp.show(img)
        # print("binary")
        img_mid = img.width() /2
        print(12321)

        print(shape)
        if shape == '0x0a':
            print('1')
            circle = Circle_find(img)
            print('2')
            disp.show(img)
            print(circle)
            if circle == None:
                continue
            if circle != None:
                object = [circle[0],circle[1],circle[2],circle[3]]   #格式为[圆心x坐标，圆心y坐标，半径]
                circle = None

                ratio = (35.5/object[2] + 35.5/object[3])/2      #mm/pixil
                print(object[1])
                # if object[0] in range(-30,30):
                distance_x = 67 - int((img_mid - object[0] - 18) * ratio *(134/99)) - 10   #需要手动添加一个摄像头与爪子中心的偏移值  #图像中心与爪子中心差距17.72个像素点  # +15为受活动调制
                print (distance_x,"\t\t",shape,"\t\t")
                if distance_x <0:
                    distance_x = 0
                elif distance_x >134:
                    distance_x = 134
                Uart(distance_x)       #让竖直得直接输出偏移量为67
                break

                
        if shape == '0x0b':
            print('3')
            rectangular = Rectangular_find(img)
            print('4')
            disp.show(img)
            print(rectangular)
            if rectangular == None:
                    continue
            if rectangular != None:
                object = rectangular
                rectangular = None
                print(7979810)
                ratio1 = 71 / object[2]
                ratio2 = 71 / object[3]
                ratio = (ratio1 + ratio2) / 2
                center = [object[0], object[1]]
                # if object[0] in range(-30,30):
                distance_x = 67 - int((img_mid - center[0] - 18 ) * ratio * (134/99)) - 10 
                print (distance_x,"\t\t",shape,"\t\t")
                if distance_x <0:
                    distance_x = 0
                elif distance_x >134:
                    distance_x = 134
                Uart(distance_x)
                break

        if shape == '0x0c':
            print('5')
            trig = Trig_find(img)
            print('6')
            disp.show(img)
            print(trig)
            if trig == None:
                continue
            if trig !=None:
                object = trig
                trig = None

                ratio = 86 / object[2]
                center = [object[0], object[1]]
                distance_x = 67 - int((img_mid - center[0] - 18) * ratio * (134/99)) - 15
                print (distance_x,"\t\t",shape,"\t\t")
                if distance_x <0:
                    distance_x = 0
                elif distance_x >134:
                    distance_x = 134
                Uart(distance_x)
                
                break

        if shape == '0x0d':
            print('7')
            trapz = Trapz_find(img)
            print('8')
            disp.show(img)
            if trapz == None:
                    continue
            if trapz !=None:
                object = trapz
                trapz = None

                ratio1 = 75 / object[2]
                ratio = (ratio1) / 2
                center = [object[0], object[1]]
                distance_x = 67 - int((img_mid - center[0] - 18) * ratio * (134/99))

                print (distance_x,"\t\t",shape,"\t\t")
                if distance_x <0:
                    distance_x = 0
                elif distance_x >134:
                    distance_x = 134
                Uart(distance_x)
                break





# #以下是识别圆的代码
# def Circle_find(img: image.Image):
#     '''
#     图像坐标为：(a.x(),a.y()),直径为 a.r() ; 或 corners (内含所识别到的红色占据图中矩形的四点坐标)
#     '''
#     circles = img.find_circles(threshold = 4000,x_margin=20,y_margin=20,r_margin=20,r_min=28,r_max=35,r_step=5)   #rmin = 45
#     #以下是识别 某种颜色圆 的代码
#     for a in circles:

#         img.draw_circle(a.x(), a.y(), a.r(), image.COLOR_RED, 2)
#         img.draw_string(a.x() + a.r() + 5, a.y() + a.r() + 5, "r: " + str(a.r()) + "magnitude: " + str(a.magnitude()), image.COLOR_RED)
#         print(a.x(),a.y(),a.r())
#         return a


#以下是识别圆的代码
def Circle_find(img: image.Image):
    global detector
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)

    for obj in objs:
        distance_x = obj.x+(obj.w/2)
        distance_y = obj.y+(obj.h/2)
        Circle = [ distance_x, distance_y, obj.w, obj.h]

        return Circle


def Rectangular_find(img: image.Image):
    global detector
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)

    for obj in objs:
        distance_x = obj.x+(obj.w/2)
        distance_y = obj.y+(obj.h/2)
        Rect = [ distance_x, distance_y, obj.w, obj.h]

        return Rect
        
def Trig_find(img:image.Image):
    global detector
    objs = detector.detect(img, conf_th = 0.3, iou_th = 0.25)
    distance_x = 0
    distance_y = 0

    for obj in objs:
        if obj.class_id == 2:
            # print('1')
            distance_x = obj.x+(obj.w/2)
            distance_y = obj.y+(obj.h/2)

            # if distance_x in range(-10,35):
            Trig = [distance_x, distance_y, obj.w, obj.h]

            return Trig

def Trapz_find(img:image.Image):
    global detector
    objs = detector.detect(img, conf_th = 0.4, iou_th = 0.4)
    distance_x = 0
    distance_y = 0

    for obj in objs:
        if obj.class_id == 1:

            distance_x = obj.x+(obj.w/2)
            distance_y = obj.y+(obj.h/2)

            # if distance_x in range(-10,35):
            Trapz = [distance_x, distance_y, obj.w, obj.h]

            return Trapz



# #以下是识别矩形的代码
# def Rectangular_find(img: image.Image):
#     '''
#     图像坐标为：[    (rect[0]        ,    rect[1]        ),
#                     (rect[0]+rect[2],    rect[1]        ),
#                     (rect[0]+rect[2],    rect[1]+rect[3]),
#                     (rect[0]        ,    rect[1]+rect[3])]  顺序为顺时针
#     '''
#     #以下是识别 某种颜色矩形 的代码 
#     #此处颜色识别效果不太好，最好应先识别矩形再判断颜色，但出于最终用颜色统一函数的需求，在此先判断颜色。使用时应将摄像头摆放在矩形大约18cm——19cm 
#     color_blobs = img.find_blobs(thresholds_color, area_threshold = 100, pixels_threshold = 100)
#     for b in color_blobs:
#             corners = b.corners()
#             RECT = b.rect()
#             rects = img.find_rects(roi=[RECT[0]-20000,RECT[1]-20000,RECT[2]+20000,RECT[3]+20000], threshold = 69500)
#             for a in rects:
#                 rect = a.rect()
#                 for i in range(4):
#                     img.draw_rect(rect[0],rect[1],rect[2],rect[3],image.COLOR_RED)
#                     img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
#                     img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_RED)
#                     img.draw_string(rect[0] + 5, rect[1] + 20, "magnitude: " + str(a.magnitude()), image.COLOR_RED)
#                     return rect

# #以下是识别三角形和梯形（近似为四边形）的代码
# def TrigATrapz_find(LAB_thresholds, img):
#     import cv2
#     import numpy as np
#     kernel = np.ones((3,3), np.uint8)        #创建核
#     i =0

#     img_raw = image.image2cv(img,ensure_bgr=False,copy=False)
#     img_ = cv2.cvtColor(img_raw,cv2.COLOR_BGR2LAB)   #RGB转LAB
#     #LAB_thresholds = [[0,71,-4,77,36,79]]    #原为红值，现为蓝值且后四项两组反转
#     #LAB_thresholds = [[0,61,-128,127,-128,-30]]     #原为蓝值，现为红值

#     # 解析LAB阈值参数（OpenCV的LAB范围特性是：L(0~255)；A(-128~127);B(-128~127)）
#     Lmin,Lmax,Amin,Amax,Bmin,Bmax = LAB_thresholds[0]   #创建LAB通道的高低

#     lower_bound = np.array([Lmin*255/100, Amin+128, Bmin+128])  #上下界限
#     upper_bound = np.array([Lmax*255/100, Amax+128, Bmax+128])
    
#     mask = cv2.inRange(img_, lower_bound, upper_bound)
#         #第一个参数：src指的是原图
#         #第二个参数：lower_red指的是图像中低于这个lower_red的值，图像值变为0
#         #第三个参数：upper_red指的是图像中高于这个upper_red的值，图像值变为0
#         #而在lower_red～upper_red之间的值变成255

#     # if LAB_thresholds[0][3] <= 70:                               #绿色时掩图就取反
#     #     mask = cv2.bitwise_not(mask)

#     #img_raw = cv2.bitwise_and(img_raw,img_raw,mask=mask)        #颜色已抓取

#     img_= cv2.GaussianBlur(mask,(5,5),0)     #高斯滤波
#     img_= cv2.bilateralFilter(img_, 9, 75, 75) #双边滤波(去噪点)
    
#     _, thresh = cv2.threshold(img_, 127, 255, cv2.THRESH_BINARY) #二值化
#     #thresh = cv2.morphologyEx(img_raw, cv2.MORPH_OPEN, kernel)
#     thresh = cv2.morphologyEx(img_, cv2.MORPH_CLOSE, kernel) #闭运算(去噪点)  
#     edged = cv2.Canny (thresh, 200, 600)    #Canny找边缘
#     contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
#     if len(contours) > 0:
#         #筛选出最大的轮廓
#         largest_contour = max(contours, key=cv2.contourArea)
    
#         epsilon =0.02 * cv2.arcLength(largest_contour,True)
#         approx = cv2.approxPolyDP(largest_contour, epsilon, True) #approxPolyDP逼近多边形   approx格式为:[[[x1 y1]] [[x2 y2]] [[x3 y3]]]
#         # if len(approx) > 10:  #如果角点数>=3
#         #     print("这是圆")
#         #     cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)
#         if len(approx) == 3:
#             # rect = cv2.minAreaRect(approx)  #获取最小外接矩形
#             # points = cv2.boxPoints(rect)     #最小外接矩形的四点(顺序：右下；左下；右上；左上)
#             # # center = rect[0]            
#             print("这是一个"+str(len(approx))+"边形")  
#             # print(points)
#             # cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)   #drawContours画出轮廓
#             for point in approx:
#                 x, y = point.ravel()    #获取每个多边形角点坐标
#                 cv2.circle(img=img_raw,center=(x,y),radius=5,color=(255,0,0),thickness=2) #circle画出多边形角点
#                 approx = approx.tolist()                                                  #approx从array转list，防止下面判断报错
#                 return approx                                                             #不测试的话就把point循环给删了，直接输出approx
                
#         elif len(approx) == 4 :
#             print("这是一个"+str(len(approx))+"边形")
#             #cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)   #drawContours画出轮廓
#             for point in approx:
#                 x, y = point.ravel()    #获取每个多边形角点坐标
#                 cv2.circle(img=img_raw,center=(x,y),radius=5,color=(255,0,0),thickness=2) #circle画出多边形角点
#                 approx = approx.tolist()
#                 return approx
