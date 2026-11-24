#----------------
#图像处理: LAB通道调参 | 高斯、双边滤波 | 开操作一次 | Canny边缘检测（慢）| Cv2库的识别角点和逼近多边形
#Img_Precessing_3.py
#功能：决赛第二部分图形识别（包括形状识别、颜色识别、位置识别）
#----------------
#2025.3.6 ———2025.
#yst2219 
#----------------
#
# 
#------------------------------------------------------------问题：

# import cv2
from maix import camera, image, display, time, nn
from UART import Uart
   
disp=display.Display() 

distance_x = 0
distance_y = 0
FFlag = 0
COUNT = 0       # COUNT是超级全局变量
# rotary_lib = {0:[("blue",'0x0a'),0],1:[("red" ,'0x0d'),0],2:[("red" ,'0x0c'),0],3:[("blue",'0x0b'),0],   #结构：key:[("图形"，图形代号)，占用flag]
#               4:[("red" ,'0x0a'),0],5:[("blue",'0x0d'),0],6:[("blue",'0x0c'),0],7:[("red" ,'0x0b'),0]}

cam = camera.Camera(200,200)       #配置摄像头
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


# def rotary_control_2(massage):              # massage 是单片机(?) 传过来的物块信息，与第一阶段发送格式相同
#     global COUNT
#     global rotary_lib   #rotary_lib = {0:[("blue",'\x0A'),0],1:[("red" ,'\x0B'),0],2:[("blue",'\x0C'),0],3:[("blue",'\x0D'),0],   #结构：key:[("图形"，图形代号)，是否已用flag]
#                         #              4:[("red" ,'\x0A'),0],5:[("blue",'\x0B'),0],6:[("red" ,'\x0C'),0],7:[("red" ,'\x0D'),0]}
#     pos_dif = 0
#     # print(massage)
#     while 1:
#         COUNT %=8
#         if massage == None:
#             # COUNT = 0
#             break
#         elif (massage[0] == rotary_lib[COUNT][0][1]) and (rotary_lib[COUNT][1] == 0):
#             Uart(pos_dif,0)
#             # print(pos_dif)
#             rotary_lib[COUNT][1] = 1
#             pos_dif = 0
#             # COUNT = 0
#             break
#         else :
#             COUNT +=1
#             pos_dif += 1    #可能此处算法会让转盘多转一个45度，若会就在Uart(pos_dif,0)前将pos_dif减1

#     return 0
    
'''
颜色切换还是太复杂了，相比于每种颜色判断都切换对应的颜色参数，能不能直接通过改变图像格式只使用一个参数？
e.g.    仅使用识别红色参数,在识别蓝色时将图像格式从RGB切换为BGR
'''

def image_processing_3(shape:str, color):
    global distance_x, FFlag
    # disp.show(img)
    while 1:
        img = cam.read()
        if color == '0x01':  #红值
            img = img.binary(thresholds_red)
            img = img.rotate(95)
            ShapeMatch(img,shape)
        elif  color == '0x02':     #蓝值
            img = img.binary(thresholds_blue)
            img = img.rotate(95)
            ShapeMatch(img,shape)
        elif color == '0x03':  #红蓝两色
            img1 = img.binary(thresholds_blue,copy = True)
            img2 = img.binary(thresholds_red, copy = True)
            img = img1.b_or(img2)
            img = img.rotate(95)
            ShapeMatch(img,shape)
        disp.show(img)
        # img_mid = img.width() /2
        # print(12321)


        # if shape == '0x0a':
        #     circle = Circle_find(img)
        #     disp.show(img)
        #     print(circle)
        #     if circle == None:
        #         continue
        #     if circle != None:
        #         object = [circle[0],circle[1],circle[2],circle[3]]   #格式为[圆心x坐标，圆心y坐标，半径]
        #         circle = None

        #         ratio = (35.5/object[2] + 35.5/object[3])/2      #mm/pixil
        #         print(object[1])
        #         # if object[0] in range(-30,30):
        #         distance_x_dif = 67 - int((img_mid - object[0] - 15) * ratio *1.4) - 10    #需要手动添加一个摄像头与爪子中心的偏移值  #图像中心与爪子中心差距17.72个像素点  # +15为受活动调制
        #         distance_y_dif = 129 + int(int(int(int(img.height()/2) - object[1] ) * int(ratio) ) * 0.33)      #此处为竖直调整坐标值 #圈数/mm系数是0.33
        #         print (distance_x_dif,"\t\t",distance_y_dif,"\t\t",shape)

        #         if distance_x_dif <0:
        #             distance_x_dif = 0
        #         elif distance_x_dif >134:
        #             distance_x_dif = 134
        #         # if distance_y_dif <0:
        #         #     distance_y_dif = 0
        #         # elif distance_y_dif >133:
        #         #     distance_y_dif = 133

        #         if FFlag <= 39:      #多次识别再输出
        #             distance_x += distance_x_dif
        #             # distance_y += distance_y_dif
        #             FFlag += 1
        #             continue
        #         else:
        #             distance_x = int (distance_x/40)
        #             # distance_y = int (distance_y/40)
        #             Uart(distance_x , b'\x00')
        #             break


        # if shape == '0x0a':     #红蓝识别有误问题，图形的识别问题，识别静止问题
        #     print('1')
        #     circle1 = Circle_find1(img)
        #     circle2 = Circle_find2(img)
        #     print('2')
        #     disp.show(img)
        #     # print(circle)
        #     if circle1 != None and circle2 != None:     #圆和梯形在识别中都会认为是圆，但圆的2方法识别率比梯形更高
        #         object = [circle2[0],circle2[1],circle2[2],circle2[3]]   #格式为[圆心x坐标，圆心y坐标，半径]
        #         circle1 = circle2 = None

        #         ratio = (35.5/object[2] + 35.5/object[3])/2      #mm/pixil
        #         print(object[1])
        #         # if object[0] in range(-30,30):
        #         distance_x = 67 + int((img_mid - object[0] + 18) * ratio *1.4) -  10  #需要手动添加一个摄像头与爪子中心的偏移值  #图像中心与爪子中心差距17.72个像素点  # +15为受活动调制
        #         # distance_y = 129 + int((((img.height()/2) - object[1])  * ratio )yifu * 0.5)      #此处为竖直调整坐标值 #圈数/mm系数是0.33
        #         print (distance_x,"\t\t",shape,"\t\t")
        #         if distance_x <0:
        #             distance_x = 0
        #         elif distance_x >125:
        #             distance_x = 125
        #         Uart(distance_x)       #让竖直得直接输出偏移量为67
        #         break

        # if shape == '0x0b':
        #     print('3')
        #     rectangular = Rectangular_find(img)
        #     print('4')
        #     disp.show(img)
        #     # print(rectangular)
        #     if rectangular == None:
        #         continue
        #     if rectangular != None:
        #         object = rectangular
        #         rectangular = None
        #         print(7979810)
        #         ratio1 = 71 / object[2]
        #         ratio2 = 71 / object[3]
        #         ratio = (ratio1 + ratio2) / 2
        #         # if object[0] in range(-30,30):
        #         distance_x_dif = 67 + int((img_mid - object[0] + 18) * ratio *(134/99))

        #         print (distance_x,"\t\t",shape,"\t\t")

        #         if distance_x <0:
        #             distance_x = 0
        #         elif distance_x >125:
        #             distance_x = 125
        #         if FFlag <= 5:      #多次识别再输出
        #             distance_x += distance_x_dif
        #             FFlag += 1
        #             continue
        #         else:
        #             distance_x = int (distance_x/6)
        #             Uart(distance_x)
        #             break

        # if shape == '0x0c':
        #     print('5')
        #     print(color)
        #     if FFlag <= 14:      #多次识别再输出
        #         # distance_x += distance_x_dif
        #         # distance_y += distance_y_dif
        #         FFlag += 1
        #         continue
        #     else:
        #         trig = Trig_find(img)
        #         print('6')
        #         disp.show(img)
        #         # print(trig)
        #         if trig == None:
        #             continue
        #         if trig != None:
        #             object = trig
        #             trig = None

        #             ratio = 100 / object[2]
        #             distance_x = 67 + int((img_mid - object[0] + 18) * ratio *(134/99)) +15
        #             print (distance_x,"\t\t",shape,"\t\t")
        #             if distance_x <0:
        #                 distance_x = 0
        #             elif distance_x >125:
        #                 distance_x = 125

        #             # if FFlag <= 14:      #多次识别再输出
        #             #     distance_x += distance_x_dif
        #             #     # distance_y += distance_y_dif
        #             #     FFlag += 1
        #             #     continue
        #             # else:
        #             # distance_x = int (distance_x/15)
        #             # distance_y = int (distance_y/40)
        #             Uart(distance_x)
        #             break

        # if shape == '0x0d':     #正方形、梯形和三角形都有向小坐标过调的问题
        #     print('7')
        #     trapz = Trapz_find(img)
        #     print('8')
        #     disp.show(img)
        #     if trapz ==None:
        #         continue
        #     if trapz !=None:
        #         object = trapz
        #         trapz = None

        #         ratio1 = 75 / object[2]
        #         ratio = (ratio1) / 2
        #         # center = [object[0], object[1]]
        #         distance_x_dif = 67 + int((img_mid - object[0] + 18) * ratio *(134/99)) 
        #         print (distance_x,"\t\t",shape,"\t\t")
        #         if distance_x <0:
        #             distance_x = 0
        #         elif distance_x >125:
        #             distance_x = 125
        #         if FFlag <= 5:      #多次识别再输出
        #             distance_x += distance_x_dif

        #             FFlag += 1
        #             continue
        #         else:
        #             distance_x = int (distance_x/6)

        #             Uart(distance_x)
        #             break

#以下是识别圆的代码
def Circle_find1(img: image.Image):
    '''
    图像坐标为：(a.x(),a.y()),直径为 a.r() ; 或 corners (内含所识别到的红色占据图中矩形的四点坐标)
    '''
    circles = img.find_circles(roi = [3,79,239,86], threshold = 1000,x_margin=20,y_margin=20,r_margin=20,r_min=32,r_max=45,r_step=5)   #rmin = 45
    #以下是识别 某种颜色圆 的代码
    for a in circles:

        img.draw_circle(a.x(), a.y(), a.r(), image.COLOR_RED, 2)
        img.draw_string(a.x() + a.r() + 5, a.y() + a.r() + 5, "r: " + str(a.r()) + "magnitude: " + str(a.magnitude()), image.COLOR_RED)
        print(a.x(),a.y(),a.r())
        return a


#以下是识别圆的代码
def Circle_find2(img: image.Image):
    global detector
    disp.show(img)
    objs = detector.detect(img, conf_th = 0.4, iou_th = 0.35)

    for obj in objs:
        if obj.class_id == 0:
            print('a')
            center_x = obj.x+(obj.w/2)
            center_y = obj.y+(obj.h/2)
            Circle = [ center_x, center_y, obj.w, obj.h]

            return Circle


def Rectangular_find(img: image.Image):
    global detector
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)

    for obj in objs:
        if obj.class_id == 1:
            center_x = obj.x+(obj.w/2)
            center_y = obj.y+(obj.h/2)
            Rect = [ center_x, center_y, obj.w, obj.h]

            return Rect
        
def Trig_find(img:image.Image):
    global detector
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    center_x = 0
    center_y = 0

    for obj in objs:
        if obj.class_id == 2:
            # print('1')
            center_x = obj.x+(obj.w/2)
            center_y = obj.y+(obj.h/2)

            # if distance_x in range(-10,35):
            Trig = [center_x, center_y, obj.w, obj.h]

            return Trig

def Trapz_find(img:image.Image):
    global detector
    objs = detector.detect(img, conf_th = 0.4, iou_th = 0.4)
    center_x = 0
    center_y = 0

    for obj in objs:
        if obj.class_id == 3:

            center_x = obj.x+(obj.w/2)
            center_y = obj.y+(obj.h/2)

            # if distance_x in range(-10,35):
            Trapz = [center_x, center_y, obj.w, obj.h]

            return Trapz


def ShapeMatch(img: image.Image,shape:str):
    global FFlag, distance_x
    import cv2
    img_cv = image.image2cv(img, ensure_bgr=False, copy=False)

    filepath1 = "/root/img/20250514cir.jpeg"
    filepath2 = "/root/img/20250514sqr.jpeg"
    filepath3 = "/root/img/20250514tri.jpeg"
    filepath4 = "/root/img/20250514tra.jpeg"

    if shape == '0x0a':
        ReImg = cv2.imread(filepath1)
        _,thresh1 = cv2.threshold(img_cv,0,255,cv2.THRESH_BINARY )
        _, thresh2 = cv2.threshold(ReImg, 0, 255, cv2.THRESH_BINARY) #二值化
        # ret,thresh2 = cv2.threshold(ReImg,127,255,0)
        edged1 = cv2.Canny (thresh1, 200, 600)    #Canny找边缘
        edged2 = cv2.Canny (thresh2, 200, 600)    #Canny找边缘
        contours1, _ = cv2.findContours(edged1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
        contours2, _ = cv2.findContours(edged2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours1 != ():
            result = cv2.matchShapes(contours1[0],contours2[0],1,0.0)
            print(result)
            if result == 0.0:
                circle = Circle_find1(img)
                if circle != None:
                    Circle = [circle.x(),circle.y(),circle.r()]
                    Uart( b'\x0A')        
            # return result

    if shape == '0x0b':
        ReImg = cv2.imread(filepath2)
        _,thresh1 = cv2.threshold(img_cv,127,255,cv2.THRESH_BINARY )
        _, thresh2 = cv2.threshold(ReImg, 127, 255, cv2.THRESH_BINARY) #二值化
        # ret,thresh2 = cv2.threshold(ReImg,127,255,0)
        edged1 = cv2.Canny (thresh1, 200, 600)    #Canny找边缘
        edged2 = cv2.Canny (thresh2, 200, 600)    #Canny找边缘
        contours1, _ = cv2.findContours(edged1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
        contours2, _ = cv2.findContours(edged2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours1 != None:
            result = cv2.matchShapes(contours1[0],contours2[0],1,0.0)
            print(result)
            if result == 0.0:
                rect = Rectangular_find(img)
                if rect != ():
                    print (distance_x,"\t\t",shape,"\t\t")
                    distance_x = int (distance_x/6)
                    Uart(b'\x0B')
            # return result

    if shape == '0x0c':
        ReImg = cv2.imread(filepath3)
        _,thresh1 = cv2.threshold(img_cv,127,255,cv2.THRESH_BINARY )
        _, thresh2 = cv2.threshold(ReImg, 127, 255, cv2.THRESH_BINARY) #二值化
        # ret,thresh2 = cv2.threshold(ReImg,127,255,0)
        edged1 = cv2.Canny (thresh1, 200, 600)    #Canny找边缘
        edged2 = cv2.Canny (thresh2, 200, 600)    #Canny找边缘
        contours1, _ = cv2.findContours(edged1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
        contours2, _ = cv2.findContours(edged2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours1 != ():
            result = cv2.matchShapes(contours1[0],contours2[0],1,0.0)
            print(result)
            if result == 0.0:
                trig = Trig_find(img)
                if trig != None:
                    Uart(b'\x0C')
            # return result
    if shape == '0x0d':
        ReImg = cv2.imread(filepath4)
        _,thresh1 = cv2.threshold(img_cv,127,255,cv2.THRESH_BINARY )
        _, thresh2 = cv2.threshold(ReImg, 127, 255, cv2.THRESH_BINARY) #二值化
        # ret,thresh2 = cv2.threshold(ReImg,127,255,0)
        edged1 = cv2.Canny (thresh1, 200, 600)    #Canny找边缘
        edged2 = cv2.Canny (thresh2, 200, 600)    #Canny找边缘
        contours1, _ = cv2.findContours(edged1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
        contours2, _ = cv2.findContours(edged2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours1 != ():
            result = cv2.matchShapes(contours1[0],contours2[0],1,0.0)
            print(result)
            if result == 0.0:
                trapz = Trapz_find(img)
                if trapz != None:
                    Uart(b'\x0D')
                # return result
