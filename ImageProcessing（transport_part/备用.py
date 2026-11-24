 





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



        # if object == None:                  #啥都没有
        #     # print('ABC')
        #     continue

        # elif object[0] == b'\x0A':          #圆形
            # # if flag_1 ==0 :                  #用于提前停下传送带
            # #     flag_1 += 1
            # #     # Uart(b'\x00',b'\x00',67,b'\x00')
            # #     time.sleep_ms(5)       #等待传送带停止
            # #     continue
            # # else:
            # ratio = 22.5 / object[2][2]     # 1mm/pixle 
            # distance_x_dif = 67 - int((100 - object[2][0]) * ratio * 1.4)     #要求物块在视野内从左到右，否则该值取相反数
            # print(distance_x_dif)
            # # if distance_x_dif in range(4,20):
            # flag_1= 0
            # while 1:        #要停得慢，识别得快，但是不能提前识别
            #     if FFFlag == 5:
            #         FFFlag += 1     #第六次时停传送带
            #         # distance_x += distance_x_dif
            #         Uart(b'\x00',b'\x00',67,b'\x00')
            #         continue
            #     elif FFFlag in range(0,5):
            #         FFFlag += 1     #空识别五次
            #         # distance_x += distance_x_dif
            #         continue
            #     elif FFFlag in range(6,10):
            #         FFFlag += 1     #空识别四次
            #         # distance_x += distance_x_dif
            #         continue
            #     elif FFFlag in range(10,111):       #加和100次
            #         FFFlag += 1
            #         distance_x += distance_x_dif
            #         continue
            #     else:
            #         # FFFlag = 0
            #         distance_x = int(distance_x/100)
            #         print(distance_x)
            #         force = object[3]
            #         if distance_x > 134:
            #             distance_x = 134
            #         elif distance_x <0:
            #             distance_x = 0
            #         Uart(object[0],force,distance_x,b'\xFC')
            #         break
                


                # print (distance_x)
                # # distance_y = int((object[2][1] - 100) * ratio)  #物块在中心点偏下，则y值为正；反之为负
                # force = object[3]
                # if distance_x > 134:
                #     distance_x = 134

                # # print (distance_x,"\t\t",distance_y,"\t\t",object[0],"\t\t")  
                # Uart(object[0],force,distance_x,b'\xFC')

            
        # elif object[0] == b'\x0B':          #正方形
        #     if flag_1 == 0:
        #         flag_1 += 1
        #         Uart(b'\x00',b'\x00',67,b'\x00')
        #         time.sleep_ms(50)       #等待传送带停止
        #         continue
        #     # if len(object[2]) != object[1] :                  #用于提前停下传送带

        #     #     Uart(b'\x00',b'\x00',67,b'\x00')
        #     #     time.sleep_ms(20)       #等待传送带停止
        #     #     continue
        #     else:
        #         # print (object)
        #         ratio = 45 / object[2][2]         # 45mm/pixle

        #         distance_x = int(object[2][0] * ratio)      #单位mm
        #         # print (distance_x)
        #         # if distance_x in range(65,130):
        #         distance_x = 67 - int((object[2][0]) * ratio *1.4)
        #         distance_y = int((object[2][1] - 100) * ratio)
        #         force = object[3]
        #         if distance_x > 134:
        #             distance_x = 134
        #         elif distance_x <0:
        #             distance_x = 0
        #         print (distance_x,"\t\t",distance_y,"\t\t",object[0],"\t\t")  

        #         Uart(object[0],force,distance_x,b'\xFC')
            
        # elif object[0] ==b'\x0C':           #三角形 [  ,  ,[ x, y, w, h],  ]
        #     if flag_1 == 0 :                 #用于提前停下传送带
        #         flag_1 += 1
        #         Uart(b'\x00',b'\x00',67,b'\x00')
        #         continue
        #     else:
        #         # print('3')
        #         ratio1 = 45 / object[2][2]
        #         ratio2 = 45 / object[2][3]
        #         ratio = (ratio1 + ratio2) / 2
        #         center = [ object[2][0], object[2][1]]

        #         distance_x = int((100 - center[0]) * ratio)
        #         # flag_1= 0
        #         print(distance_x)
        #         # if distance_x in range(-45,-22):
        #         distance_x = 67 - int((100 - center[0]) * ratio * 1.4)  + 20 #减1或加1都会导致偏向喻，但是数值为9时便会夹取正中间（虽然放置时会偏喻
        #         distance_y = 67 - int((100 - center[1]) * ratio *1.4)
        #         force = object[3]
        #         print (distance_x,"\t\t",distance_y,"\t\t",object[0],"\t\t")
        #         # time.sleep_ms(1000)
        #         Uart(object[0],force,distance_x,b'\xFC')
                        
        # elif object[0] ==b'\x0C':           #三角形 [  ,  ,[ x, y, w, h],  ]
        #     # if flag_1 == 0 :                 #用于提前停下传送带
        #     #     Uart(b'\x00',b'\x00',67,b'\x00')
        #     #     flag_1 += 1

        #     #     # time.sleep_ms(50)
        #     #     continue
        #     # else:
        #         # print('3')
        #     ratio1 = 45 / object[2][2]
        #     ratio2 = 45 / object[2][3]
        #     ratio = (ratio1 + ratio2) / 2
        #     center = [ object[2][0], object[2][1]]

        #     # distance_x = int((100 - center[0]) * ratio)
        #     # flag_1= 0
        #     # if distance_x in range(-45,-22):
        #     distance_x = 67 - int((100 - center[0]) * ratio * 1.4)  #减1或加1都会导致偏向喻，但是数值为9时便会夹取正中间（虽然放置时会偏喻
        #     print(distance_x)
        #     # distance_y = 67 - int((100 - center[1]) * ratio *1.4)
        #     force = object[3]

        #     if distance_x > 134:
        #         distance_x = 134
        #     elif distance_x <0:
        #         distance_x = 0
        #     # print (distance_x,"\t\t",distance_y,"\t\t",object[0],"\t\t")    
        #     Uart(object[0],force,distance_x,b'\xFC')

        # elif object[0] ==b'\x0D':           #梯形 [  ,  ,[ x, y, w, h],  ]
        #     if flag_1 == 0:
        #         flag_1 += 1
        #         Uart(b'\x00',b'\x00',67,b'\x00')
        #         time.sleep_ms(500)
        #         continue
        #     else:
        #         ratio1 = 45 / object[2][2]
        #         ratio2 = 45 / object[2][3]
        #         ratio = (ratio1 + ratio2) / 2
        #         center =  [ object[2][0], object[2][1]]

        #         # distance_x = int((100 - center[0]) * ratio)
        #         # if distance_x in range(-20,20):
        #         distance_x = 67 - int((100 - center[0]) * ratio * 1.4)+25
        #         print(distance_x)
        #         distance_y = int((100 - center[1]) * ratio)
        #         force = object[3]
        #         if distance_x > 134:
        #             distance_x = 134
        #         elif distance_x <0:
        #             distance_x = 0
        #         print (distance_x,"\t\t",distance_y,"\t\t",object[0],"\t\t")  
        #         Uart(object[0],force,distance_x,b'\xFC')


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


''' 建议用二值化数组中间行检测的方法判定三角， 记得先去binary代码里面试试'''#试过了，你个sb，逻辑整体行不通的
# from maix import camera, display, app, time, image
# import numpy as np

# cam = camera.Camera(200, 200)
# disp = display.Display()


# thresholds = [[66,100,-19,17,-10,2]]
# while not app.need_exit():
#     time.fps_start()
#     img = cam.read()
#     img.binary(thresholds)
#     imgcv = image.image2cv(img)
#     middle_row = imgcv[100, :]
#     sum_raw = middle_row.sum()
#     print(sum_raw)
#     disp.show(img)
#     fps = time.fps()
#     print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")


def main():
    Image_Processing()




if __name__ == "__main__":
    main()

