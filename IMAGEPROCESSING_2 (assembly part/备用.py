 





from maix import image, camera, display, app, time
import numpy as np 
import cv2

cam = camera.Camera(200,200)
cam.skip_frames(30)   
disp=display.Display()
kernel = np.ones((3,3), np.uint8)


while not app.need_exit():
    img = cam.read()
    #img = img.lens_corr(strength=1.5)                                                  #畸变矫正（占算力，且识别结果不佳）
    
    img_raw = image.image2cv(img,ensure_bgr=False,copy=False)
    img_ = cv2.cvtColor(img_raw,cv2.COLOR_BGR2LAB)                                      #RGB转LAB

    #img_raw = cv2.cvtColor(img_raw,cv2.COLOR_BGR2LAB)
    #LAB_thresholds = [[0,71,-4,77,36,79]]                                              #原为红值，现为蓝值且后四项两组反转
    LAB_thresholds = [[0,61,-128,127,-128,-30]]                                         #原为蓝值，现为红值
    #LAB_thresholds= [[0,80,-118,-15,2,127]]                                            #原为绿值，现也为绿值

    # 解析LAB阈值参数（OpenCV的LAB范围特性是：L(0~255)；A(-128~127);B(-128~127)）
    Lmin,Lmax,Amin,Amax,Bmin,Bmax = LAB_thresholds[0]                                   #创建LAB通道的高低
    
    lower_bound = np.array([Lmin*255/100, Amin+128, Bmin+128])
    upper_bound = np.array([Lmax*255/100, Amax+128, Bmax+128])
    
    mask = cv2.inRange(img_, lower_bound, upper_bound)   #几乎全黑  
                                                                                        #第一个参数：src指的是原图
                                                                                        #第二个参数：lower_red指的是图像中低于这个lower_red的值，图像值变为0
                                                                                        #第三个参数：upper_red指的是图像中高于这个upper_red的值，图像值变为0
                                                                                        #而在lower_red～upper_red之间的值变成255
    

    img_= cv2.GaussianBlur(mask,(5,5),0)                                                #高斯滤波
    img_= cv2.bilateralFilter(img_, 9, 75, 75)                                          #双边滤波(去噪点)
    
    _, thresh = cv2.threshold(img_, 127, 255, cv2.THRESH_BINARY)                        #二值化
    thresh = cv2.morphologyEx(img_, cv2.MORPH_CLOSE, kernel)                            #闭运算(去噪点)
    edged = cv2.Canny (thresh, 200, 600)                                                #Canny找边缘
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)   #findContours找角点
    if len(contours) > 0:
        #筛选出最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
    
        epsilon =0.02 * cv2.arcLength(largest_contour,True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)                       #approxPolyDP逼近多边形
        if len(approx) >= 15:  #如果角点数>=3
            print("这是圆")
            cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)
        elif len(approx) == 3:
            rect = cv2.minAreaRect(approx)                                              #获取最小外接矩形
            points = cv2.boxPoints(rect)                                                #最小外接矩形的四点(顺序：右下；左下；右上；左上)
            center = rect[0]            
            print("这是一个"+str(len(approx))+"边形")  
            print(points)
            cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)                      #drawContours画出轮廓
            for point in approx:
                x, y = point.ravel()                                                    #获取每个多边形角点坐标
                cv2.circle(img=img_raw,center=(x,y),radius=5,color=(255,0,0),thickness=2) #circle画出多边形角点
        elif len(approx) == 4 or len(approx) == 5:
            print("这是一个"+str(len(approx))+"边形")
            cv2.drawContours(img_raw, [approx], 0, (0, 255, 0), 3)                      #drawContours画出轮廓
            for point in approx:
                x, y = point.ravel()                                                    #获取每个多边形角点坐标
                cv2.circle(img=img_raw,center=(x,y),radius=5,color=(255,0,0),thickness=2) #circle画出多边形角点
    
       
    img_show = image.cv2image(img_raw,bgr=False,copy=False)                             #将图像转换为maix格式
    
    disp.show(img_show)                                                                 #输出图像 
    fps = time.fps()                                                                    # | 计算两次 fps 函数调用之间的帧率
    print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")                                  # | 在终端打印帧率（FPS）








    from maix import camera, display, image,app,time
import numpy as np
import cv2


cam = camera.Camera(200, 200)
cam.skip_frames(30) 
disp = display.Display()
kernel = np.ones((3,3), np.uint8)        #创建核


thresholds_red = [[0,71,36,79,-4,77]]        #red LAB
thresholds_blue = [[0,61,-128,127,-128,-30]]    #blue LAB
thresholds_green = [[0,80,-118,-15,2,127]]     #green LAB#识别履带
#thresholds_green = [[21,41,-34,-14,-5,15]]     #green LAB#识别履带(自动采的也不知道好不好)

def Image_Processing():
    #以下是识别圆的代码
    '''图像坐标为：(a.x(),a.y()),直径为 a.r() ; 或 corners (内含所识别到的红色占据图中矩形的四点坐标)'''
    '''
    while 1:
        img = cam.read()
        circles = img.find_circles(threshold = 4000,x_margin=20,y_margin=20,r_margin=20,r_min=45,r_max=62,r_step=5)
        
        #以下是识别红色圆的代码
        red_blobs = img.find_blobs(thresholds_red, area_threshold = 100, pixels_threshold = 100)
        for b in red_blobs:
            corners = b.corners()
            for a in circles:
                for i in range(4):
                    img.draw_circle(a.x(), a.y(), a.r(), image.COLOR_RED, 2)
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
                    img.draw_string(a.x() + a.r() + 5, a.y() + a.r() + 5, "r: " + str(a.r()) + "magnitude: " + str(a.magnitude()), image.COLOR_RED)
    

        #以下是识别蓝色圆的代码

        blue_blobs = img.find_blobs(thresholds_blue, area_threshold = 100, pixels_threshold = 100)
        for b in blue_blobs:
            corners = b.corners()
            for a in circles:
                for i in range(4):
                    img.draw_circle(a.x(), a.y(), a.r(), image.COLOR_RED, 2)
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
                    img.draw_string(a.x() + a.r() + 5, a.y() + a.r() + 5, "r: " + str(a.r()) + "magnitude: " + str(a.magnitude()), image.COLOR_RED)
                    print(a.x(),a.y(),a.r())
        disp.show(img)
        fps = time.fps()            # Calculate FPS between last time fps() call and this time call.
                                    # | 计算两次 fps 函数调用之间的帧率
        print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}") # print FPS in console
                                                        # | 在终端打印帧率（FPS）
    '''
    
    #以下是识别矩形的代码
    '''图像坐标为：[    (rect[0]        ,    rect[1]        ),
                    (rect[0]+rect[2],    rect[1]        ),
                    (rect[0]+rect[2],    rect[1]+rect[3]),
                    (rect[0]        ,    rect[1]+rect[3])]  顺序为顺时针
    '''
    '''
    while 1:
        img = cam.read()

        #以下是识别红色矩形的代码 
        #此处颜色识别效果不太好，最好应先识别矩形再判断颜色，但出于最终用颜色统一函数的需求，在此先判断颜色。使用时应将摄像头摆放在矩形大约18cm——19cm 
        red_blobs = img.find_blobs(thresholds_red, area_threshold = 100, pixels_threshold = 100)
        for b in red_blobs:
            corners = b.corners()
            RECT = b.rect()
            rects = img.find_rects(roi=[RECT[0]-20000,RECT[1]-20000,RECT[2]+20000,RECT[3]+20000], threshold = 69500)
            for a in rects:
                rect = a.rect()
                for i in range(4):
                    img.draw_rect(rect[0],rect[1],rect[2],rect[3],image.COLOR_RED)
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
                    img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_RED)
                    img.draw_string(rect[0] + 5, rect[1] + 20, "magnitude: " + str(a.magnitude()), image.COLOR_RED)
        disp.show(img)
        #以下是识别蓝色矩形的代码

        #第一种(可能会误测到周边环境)
        blue_blobs = img.find_blobs(thresholds_blue, area_threshold = 100, pixels_threshold = 100)
        rects = img.find_rects(threshold = 69500)
        for b in red_blobs:
            corners = b.corners()
            RECT = b.rect()
            for a in rects:
                rect = a.rect()
                for i in range(4):
                    img.draw_rect(rect[0],rect[1],rect[2],rect[3],image.COLOR_RED)
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
                    img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_RED)
                    img.draw_string(rect[0] + 5, rect[1] + 20, "magnitude: " + str(a.magnitude()), image.COLOR_RED)
        
        #第二种（反应很慢，但准）
        blue_blobs = img.find_blobs(thresholds_blue, area_threshold = 100, pixels_threshold = 100)
        for b in red_blobs:
            corners = b.corners()
            RECT = b.rect()
            rects = img.find_rects(roi=[RECT[0]-20000,RECT[1]-20000,RECT[2]+20000,RECT[3]+20000], threshold = 69500)
            for a in rects:
                rect = a.rect()
                for i in range(4):
                    img.draw_rect(rect[0],rect[1],rect[2],rect[3],image.COLOR_RED)
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
                    img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_RED)
    '''    
        



    #以下是识别三角形和梯形（近似为四边形）的代码
    '''
    while 1:
        img = cam.read()
        red_blobs = img.find_blobs(thresholds_red, area_threshold = 100, pixels_threshold = 100)
        for b in red_blobs:
            corners = b.corners()
            trig = find_polygon(img)  #img为待处理图像,3为所要找的多边形角点数
            trapz = find_polygon(img)
            print(trig)
            disp.show(trig) #输出一次开运算的图像5秒 
        
    '''
    #img.to_format(image.Format.FMT_GRAYSCALE)

    # import cv2
    # import numpy as np
    # from math import atan, degrees
    # k_sum = 0
    # kernel = np.ones((3,3), np.uint8)   #搞个核
    # time.fps_start()          # Manually set fps calculation start point, comment here mean last time fps() call is start
    #                             # | 动设置帧率（FPS）计算开始点，这里注释了表示上一次 fps 函数即是开始
    # img = img.crop(x = 0, y = 100, w = 200, h = 100)    #图像高度减半，减少计算量
    # #以下为找目标色块（红蓝无区分）
    # img_cv = img.image2cv(img = img, ensure_bgr = False, copy = False)
    # img_cv = cv2.cvtColor(img_cv,cv2.COLOR_RGB2BGR)
    # img_cv = cv2.cvtColor(img_cv,cv2.COLOR_BGR2LAB)
    # # img_height ,img_width = img.shape[:2]
    # Lmin,Lmax,Amin,Amax,Bmin,Bmax = thresholds_blue[0]  #创建LAB通道的高低
    # Lmin1,Lmax1,Amin1,Amax1,Bmin1,Bmax1 = thresholds_red[0]   

    # lower_bound1 = np.array([Lmin*255/100, Amin+128, Bmin+128])  #上下界限1
    # upper_bound1 = np.array([Lmax*255/100, Amax+128, Bmax+128])
    # lower_bound2 = np.array([Lmin1*255/100, Amin1+128, Bmin1+128])  #上下界限2
    # upper_bound2 = np.array([Lmax1*255/100, Amax1+128, Bmax1+128])

    # mask1 = cv2.inRange(img, lower_bound1, upper_bound1)    
    # mask2 = cv2. inRange(img,lower_bound2,upper_bound2)
    # mask = cv2.bitwise_or(mask1,mask2)                              #合成红蓝掩码

    # mask = np.expand_dims(mask,axis = 2)
    # mask = cv2.merge([mask,mask,mask])
    # # colorfind = cv2.bitwise_and(img,mask)                         #用于查看合并后的图像如何
    # img_= cv2.GaussianBlur(mask,(5,5),0)     #高斯滤波
    # img_= cv2.bilateralFilter(img_, 9, 75, 75) #双边滤波(去噪点)
    # thresh = cv2.morphologyEx(img_, cv2.MORPH_OPEN, kernel) #闭运算(去噪点)  
    # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel) #闭运算(去噪点)  
    
    # #以下为形状并行项
    # if shape == '0x0a':

    #     object = [3,[circle.x(),circle.y(),circle.r()]]   #格式为[参数数量，参数列表，力度]
    #     circle = None
    #     return object
    # elif shape == '0x0b':
    #     object = [3,[circle.x(),circle.y(),circle.r()]]   #格式为[参数数量，参数列表，力度]
    #     circle = None
    #     return object
    # elif shape == '0x0c':
    #     return object
    # elif shape == '0x0d':
    #     return object
    # edges = cv2.Canny( thresh, 200, 600)
    # contours,hierarchy= cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
    # largest_contour = max(contours, key=cv2.contourArea)

    # LeftPol_point = min(largest_contour,key = lambda x:x[0][0])
    # RightPol_point = max(largest_contour,key = lambda x:x[0][0])
    # UpPol_point = min(largest_contour,key = lambda x:x[0][1])
    # DownPol_point = max(largest_contour,key = lambda x:x[0][1])
    
    # for i in range(0,len(largest_contour)-3,3):
    #     point_1=largest_contour[i]
    #     x1 = point_1[0][0]
    #     y1 = point_1[0][1]
    #     point_2=largest_contour[i+1]
    #     x2 = point_2[0][0]
    #     y2 = point_2[0][1]
    #     point_3=largest_contour[i+2]
    #     x3 = point_3[0][0]
    #     y3 = point_3[0][1]
    #     if y1==y2 or y2==y3:
    #         continue
    #     k1 = (x1-x2)/(y1-y2)
    #     k2 = (x2-x3)/(y2-y3)
    #     k3 = (x1-x3)/(y1-y3)
    #     k_avg = (k1+k2)/2
    #     k_sum += k_avg
    
    # if k_sum in range(-2,0):
    #     print("circle") 


def main():
    Image_Processing()




if __name__ == "__main__":
    main()

'''
def Uart(info_send1,info_send2,info_send3):
    devices = uart.list_devices()
    serial = uart.UART(devices[0], 115200, uart.BITS.BITS_8, uart.PARITY.PARITY_NONE, uart.STOP.STOP_1)  
    
    # num = 10
    bytes_content = b'\xFE'     #信号开头
    bytes_content += b'\xAA'     #传送带停止指令
    bytes_content += pack("<h",info_send1)      #用char类型会溢出，只能用两个字节
    # bytes_content += pack("<i", num)  #将字符串转成二进制数据

    bytes_content += pack("<h",info_send2)     #一个数值传输量 
    bytes_content += info_send3
    bytes_content += b'\xFF'
    print(bytes_content, type(bytes_content))
    serial.write(bytes_content)
'''

'''
#以下是处理圆的代码
def Circle_proc(objects: list):
    
    # object = [b'\x01',3,[circle.x(),circle.y(),circle.r()]]
    
    ratio = object[2][2] / 225     # pixel / 0.1mm 
    distance_x = int((100 - object[2][0]) * ratio) + 730    #要求物块在视野内从左到右，否则该值取相反数
    distance_y = int((100 - object[2][1]) * ratio)
    # Info_Processing( distance_x, distance_y)
    print (distance_x,"\t\t",distance_y,"\t\t")
    # time.sleep_ms(1000)
    Uart(distance_x,distance_y)
'''

'''
#以下是处理矩形的代码
def Rectangular_proc(objects: lis):
    
    # object = [b'\x02',4,rectangular]   #rectangular 格式为[x,y(左上点坐标),w(宽度),h(高度)]
    
    ratio = object[2][2] / 225
    ratio += object[2][3] /225
    ratio = ratio / 2
    distance_x = int((100 - object[2][0] - 0.5*object[2][2]) * ratio) + 730
    distance_y = int((100 - object[2][1] - 0.5*object[2][3]) * ratio)

    Uart(distance_x,distance_y)
'''

'''
#以下是处理三角形的代码和梯形（近似为四边形）的代码
def Trig_proc(object:list):

    # object = [b'\x03',3,[trig_a_trapz[0][0],trig_a_trapz[1][0],trig_a_trapz[2][0]]]

    x1 = object[2][0][0]
    x2 = object[2][1][0]
    x3 = object[2][2][0]
    y1 = object[2][0][1]
    y2 = object[2][1][1]
    y3 = object[2][2][1]
    center = [int(x1/3+x2/3+x3/3), int(y1/3+y2/3+y3/3)]
    ratio = (((x1-x2) ** 2+(y1-y2) ** 2) ** 0.5) / 450 
    distance_x = int((100 - center[0]) * ratio) + 730
    distance_y = int((100 - center[1]) * ratio)

    Uart(distance_x,distance_y)
'''

'''
#以下是处理梯形的代码
def Trapz_proc(object:list):

    # object = [b'\04',4,[trig_a_trapz[0][0],trig_a_trapz[1][0],trig_a_trapz[2][0],trig_a_trapz[3][0]]]

    x1 = object[2][0][0]
    x2 = object[2][1][0]
    x3 = object[2][2][0]
    x4 = object[2][3][0]
    y1 = object[2][0][1]
    y2 = object[2][1][1]
    y3 = object[2][2][1]
    y4 = object[2][3][1]
    center = [int(x1/4+x2/4+x3/4+x4/4),int(y1/4+y2/4+y3/4+y4/4)]
    ratio = (((x1-center[0]) ** 2+(y1-center[1]) ** 2) ** 0.5) / 270    #270mm 为梯形角点到重心的距离
    distance_x = int((100 - center[0]) * ratio) + 730
    distance_y = int((100 - center[1]) * ratio)

    Uart(distance_x,distance_y)
'''

'''   
def image_processing(img):

    circle = Circle_find(thresholds_object1, img)
    rectangular = Rectangular_find(thresholds_object2, img)
    if circle != None:
        object = [b'\x01',3,[circle.x(),circle.y(),circle.r()]]   #格式为[形状，参数数量，参数列表]
        circle = None
        
        fps = time.fps()                # Calculate FPS between last time fps() call and this time call.
                                        # | 计算两次 fps 函数调用之间的帧率
        print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")  #在终端打印帧率 (FPS)

        return object
    
    elif rectangular !=None:
        object = [b'\x02',4,rectangular]
        rectangular = None
        fps = time.fps()                # Calculate FPS between last time fps() call and this time call.
                                        # | 计算两次 fps 函数调用之间的帧率
        print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")  #在终端打印帧率 (FPS)

        return object
 
    # else:
    #     trig_a_trapz = TrigATrapz_find(thresholds_object1, img)
    #     if trig_a_trapz != None:
    #         if len(trig_a_trapz) == 3:
    #             object = [b'\x03',3,[trig_a_trapz[0][0],trig_a_trapz[1][0],trig_a_trapz[2][0]]]
    #             trig_a_trapz = None
    #             fps = time.fps()                # Calculate FPS between last time fps() call and this time call.
    #                                             # | 计算两次 fps 函数调用之间的帧率
    #             print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")  #在终端打印帧率 (FPS)
                
    #             return object
    #         else:
    #             object = [b'\04',4,[trig_a_trapz[0][0],trig_a_trapz[1][0],trig_a_trapz[2][0],trig_a_trapz[3][0]]]
    #             trig_a_trapz = None
    #             fps = time.fps()                # Calculate FPS between last time fps() call and this time call.
    #                                             # | 计算两次 fps 函数调用之间的帧率
    #             print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")  #在终端打印帧率 (FPS)

    #             return object
    

    disp.show(img)
'''

'''
def Image_Processing():
    while 1:
        img = cam.read()

        disp.show(img)
        #以下是识别蓝色矩形的代码
        #第一种(可能会误测到周边环境)
        blue_blobs = img.find_blobs(thresholds_blue, area_threshold = 100, pixels_threshold = 100)
        rects = img.find_rects(threshold = 69500)
        for b in blue_blobs:
            corners = b.corners()
            RECT = b.rect()
            for a in rects:
                rect = a.rect()
                for i in range(4):
                    img.draw_rect(rect[0],rect[1],rect[2],rect[3],image.COLOR_RED)
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
                    img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_RED)
                    img.draw_string(rect[0] + 5, rect[1] + 20, "magnitude: " + str(a.magnitude()), image.COLOR_RED)      
        #第二种（反应很慢，但准）
        blue_blobs = img.find_blobs(thresholds_blue, area_threshold = 100, pixels_threshold = 100)
        for b in blue_blobs:
            corners = b.corners()
            RECT = b.rect()
            rects = img.find_rects(roi=[RECT[0]-20000,RECT[1]-20000,RECT[2]+20000,RECT[3]+20000], threshold = 69500)
            for a in rects:
                rect = a.rect()
                for i in range(4):
                    img.draw_rect(rect[0],rect[1],rect[2],rect[3],image.COLOR_RED)
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE)
                    img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_RED)
        
    #以下是识别三角形和梯形（近似为四边形）的代码
    while 1:
        img = cam.read()
        red_blobs = img.find_blobs(thresholds_red, area_threshold = 100, pixels_threshold = 100)
        for b in red_blobs:
            corners = b.corners()
            trig = find_polygon(img)  #img为待处理图像,3为所要找的多边形角点数
            trapz = find_polygon(img)
            print(trig)
            disp.show(trig) #输出一次开运算的图像5秒   
'''    






def image_processing_3(shape:str, color):
    global distance_x, FFlag
    # disp.show(img)
    while 1:
        img = cam.read()
        if color == '0x01':  #红值
            img = img.binary(thresholds_red)
            img = img.rotate(95)

        elif  color == '0x02':     #蓝值
            img = img.binary(thresholds_blue)
            img = img.rotate(95)

        disp.show(img)
        img_mid = img.width() /2
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


        if shape == '0x0a':     #红蓝识别有误问题(已解决），图形的识别问题，识别静止问题
            print('1')
            while 1:
                circle = Circle_finding(img)
                print('2')
                if circle:
                    if FFlag <5:
                        FFlag += 1
                    else:
                        Uart(b'\x0A')
                        break
            # disp.show(img)
            # # print(circle)
            # if circle != None:     #圆和梯形在识别中都会认为是圆，但圆的2方法识别率比梯形更高
            #     object = [circle[0],circle[1],circle[2]]     #格式为[圆心x坐标，圆心y坐标，半径]
            #     # object = [circle2[0],circle2[1],circle2[2],circle2[3]]   #格式为[圆心x坐标，圆心y坐标，最小外接矩形长，最小外接矩形宽]
            #     circle = None

            #     ratio = 35.5/object[2]      #mm/pixil
            #     print(object[1])
            #     # if object[0] in range(-30,30):
            #     # distance_x = 67 + int((img_mid - object[0] + 18) * ratio *1.4) -  10  #需要手动添加一个摄像头与爪子中心的偏移值  #图像中心与爪子中心差距17.72个像素点  # +15为受活动调制
            #     # distance_y = 129 + int((((img.height()/2) - object[1])  * ratio )yifu * 0.5)      #此处为竖直调整坐标值 #圈数/mm系数是0.33
            #     # print (distance_x,"\t\t",shape,"\t\t")
            #     # if distance_x <0:
            #     #     distance_x = 0
            #     # elif distance_x >125:
            #     #     distance_x = 125
            #     Uart(b'\x0A')       #让竖直得直接输出偏移量为67


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
        #         if FFlag <= 3:      #多次识别再输出
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

        # if shape == '0x0d':     #正方形、梯形和三角形都有向小坐标过调的问题，根源在模型准确度不高
            print('7')
            trapz = Trapz_find(img)
            print('8')
            disp.show(img)
            if trapz ==None:
                continue
            if trapz !=None:
                object = trapz
                trapz = None

                ratio1 = 75 / object[2]
                ratio = (ratio1) / 2
                # center = [object[0], object[1]]
                distance_x_dif = 67 + int((img_mid - object[0] + 18) * ratio *(134/99)) 
                print (distance_x,"\t\t",shape,"\t\t")
                if distance_x <0:
                    distance_x = 0
                elif distance_x >125:
                    distance_x = 125
                if FFlag <= 5:      #多次识别再输出
                    distance_x += distance_x_dif

                    FFlag += 1
                    continue
                else:
                    distance_x = int (distance_x/6)

                    Uart(distance_x)
                    break



def Circle_finding(img:image.Image):
    import cv2
    import numpy as np
    kernel = np.ones((3,3), np.uint8)        #创建核
    i =0

    img_raw = image.image2cv(img,ensure_bgr=False,copy=False)
    print(img_raw)
    _, thresh = cv2.threshold(img_raw, 127, 255, cv2.THRESH_BINARY) #二值化
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel) #闭运算(去噪点)  
    edged = cv2.Canny (thresh, 200, 600)    #Canny找边缘
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #findContours找角点
    if len(contours) > 0:
        #筛选出最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
    
        epsilon =0.02 * cv2.arcLength(largest_contour,True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True) #approxPolyDP逼近多边形   approx格式为:[[[x1 y1]] [[x2 y2]] [[x3 y3]]]
        if len(approx) > 5:  #如果角点数>=3
            return True
