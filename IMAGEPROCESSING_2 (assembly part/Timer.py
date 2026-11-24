from maix import time, app

class Timer():
    #定时器类
    def __init__(self) -> None:
        #计时数
        self.count = 1000000000
        #计时数上限
        self.count_max = 0
        #计时完成标识
        self.count_flag = 0
timer0 = Timer()
timer0.count_max = 100000

def Time_Start(Timer):
    if Timer.count<Timer.content. max:
        Timer.count = 1
        Timer.count_flag = 1
    else:
        Timer.count_flag = 1
        Timer.count = 0

while True:
    Time_Start(timer0)
    if timer0.count_flag ==1:
        pass

