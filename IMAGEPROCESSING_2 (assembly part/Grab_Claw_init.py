

#以下是测量爪子中心点的直线代码

from maix import camera, display, image,time
import math

cam = camera.Camera(200, 200)
disp = display.Display()

threshold = 2000

while 1:
    time.fps_start()
    img = cam.read()
    img = img.lens_corr(strength=1.5)
    lines = img.find_lines(threshold=2000)
    for a in lines:
        img.draw_line(a.x1(), a.y1(), a.x2(), a.y2(), image.COLOR_RED, 2)
        y = int((a.y1()+a.y2())/2)
        if y in range(30,45) and a.y1() in range(30,45) and a.y2() in range(30,45):
            print(a.x1(),a.y1(), a.x2(), a.y2())
            theta = a.theta()
            rho = a.rho()
            angle_in_radians = math.radians(theta)
            x = int(math.cos(angle_in_radians) * rho)
            y = int(math.sin(angle_in_radians) * rho)
            img.draw_line(0, 0, x, y, image.COLOR_GREEN, 2)
            img.draw_string(x, y, "theta: " + str(theta) + "," + "rho: " + str(rho), image.COLOR_GREEN)
    fps = time.fps()            # Calculate FPS between last time fps() call and this time call.
                                # | 计算两次 fps 函数调用之间的帧率
    print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")
    disp.show(img)


#以下是十字边缘检测的代码
from maix import image, display, time,camera

cam = camera.Camera(200, 200)       #配置摄像头
disp = display.Display()
def cross_recog(img):
    img = img.find_edges(img, roi = [0,0, 200,100], thresholds = [100,100])
    img = img.lines

    disp.show(img)

while 1:
    img = cam.read()
    cross_recog(img)


img = image.find_blobs(thresholds = [[0,71,36,79,-4,77]])