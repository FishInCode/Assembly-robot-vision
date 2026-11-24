
from maix import uart
from struct import pack
from numpy import info



SUBF = None          #使用SUBF内的值时，将Startframe置零

device = "/dev/ttyS0"
serial0 = uart.UART(device, 115200, uart.BITS.BITS_8, uart.PARITY.PARITY_NONE, uart.STOP.STOP_1) 

def received(serial : uart.UART):
    global Startframe
    global SUBF
    SUBF = None
    data = serial.read()
    # print(data)
    if data != b'':
        data = [f"0x{byte:02x}" for byte in data]
        # if (Startframe == 0):
        SUBF = data
        Startframe = 1
        return SUBF

def Uart(info_send1):        #此处info_send1是转的角度，而info_send2是左右移动距离
 
    device = "/dev/ttyS0"
    serial0 = uart.UART(device, 115200, uart.BITS.BITS_8, uart.PARITY.PARITY_NONE, uart.STOP.STOP_1)
    # num = 10
    bytes_content = b'\x04'     #信号开头

    # bytes_content += pack(">B",info_send2)                     #竖直方向上移动到的坐标值
    # bytes_content += pack(">B",info_send1)      #左右移动方向上的坐标值     #用char类型会溢出，只能用两个字节(?)
    bytes_content += info_send1
    # bytes_content += pack("<i", num)  #将字符串转成二进制数据
    #     bytes_content += pack(">B",info_send2)     #一个数值传输量      #注意系数为mm/电机轴坐标=1.4
    bytes_content += b'\xFB'
    print(bytes_content, type(bytes_content))
    serial0.write(bytes_content)


# def Order(order_content):
#     device = "/dev/ttyS0"
#     serial = uart.UART(device, 115200, uart.BITS.BITS_8, uart.PARITY.PARITY_NONE, uart.STOP.STOP_1)

#     # order_content = b'\xAA'   #后续决定要发什么信息在写这个处理
#     print(order_content)
#     serial.write(order_content)

