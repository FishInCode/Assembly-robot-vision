         
from maix import  uart, pinmap,time
from struct import pack

from numpy import info
pinmap.set_pin_function("A16", "UART0_TX")
pinmap.set_pin_function("A17", "UART0_RX")
devices = uart.list_devices()
serial = uart.UART(devices[0], 115200, uart.BITS.BITS_8, uart.PARITY.PARITY_NONE, uart.STOP.STOP_1) 

def Uart(info_send1,info_send3, info_send4):       #格式：[0x01,0xBB,形状，distance_x,力度，0xFE]
    devices = uart.list_devices()
    serial = uart.UART(devices[0], 115200, uart.BITS.BITS_8, uart.PARITY.PARITY_NONE, uart.STOP.STOP_1)  
    
    bytes_content = b'\x03'     #信号开头
    bytes_content += b'\xBB'     #传送带停止指令

    bytes_content += info_send1     #发送形状
    # bytes_content += info_send2     #发送力度
    bytes_content += pack(">B",info_send3)             #基础值加上传输的X轴偏差量
    bytes_content += info_send4     #发送止符
    print(bytes_content, type(bytes_content))

    # print('4')
    serial.write(bytes_content)

# def on_received(serial : uart.UART, data :bytes):
#     global received_info
#     print("received:", data)
#     # if (data[0] == b'\x01'):
#     #     for i in range(1,7,1):
#     #         received_info[i-1] = data[i]
#     # send back
#     serial.write(data)
#     print("sent", data)


# def Order():
#     devices = uart.list_devices()
#     serial = uart.UART(devices[0], 115200, uart.BITS.BITS_8, uart.PARITY.PARITY_NONE, uart.STOP.STOP_1)

#     order_content = b'\xAA'   #现在尚未确定命令电机运动的校验码为何，先空着

#     serial.write(order_content)
