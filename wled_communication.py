import socket
from led import LedManager

class WledCommunicationManager:
    WLED_IP_ADDRESS_DEFAULT = '192.168.1.172'
    WLED_UDP_PORT_DEFAULT = 21324

    # https://kno.wled.ge/interfaces/udp-realtime/#udp-realtime
    WLED_PROTOCOL_WARLS = 1
    WLED_PROTOCOL_DNRGB = 4
    WLED_PROTOCOL_DEFAULT = WLED_PROTOCOL_WARLS
    NORMAL_MODE_RETURN_WAIT_SECONDS_MAX = 255
    NORMAL_MODE_RETURN_WAIT_SECONDS_SHORT = 1

    def __init__(self, led_manager: LedManager, n_leds: int, led_protocol: int = None) -> None:
        self.__led_manager: LedManager = led_manager
        self.__n_leds: int = n_leds
        self.__led_protocol: int = led_protocol or self.WLED_PROTOCOL_DEFAULT
        self.__socket: socket.socket = None

    @staticmethod
    def create_socket() -> socket.socket:
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __create_message_header_array(self) -> list[int]:
        return [self.__led_protocol, self.NORMAL_MODE_RETURN_WAIT_SECONDS_MAX]

    def __send_udp_message(self, message_array):
        self.__socket.sendto(bytearray(message_array), (self.WLED_IP_ADDRESS_DEFAULT, self.WLED_UDP_PORT_DEFAULT))

    def __reset_leds(self):
        msg = self.__create_message_header_array()
        if self.__led_protocol == self.WLED_PROTOCOL_DNRGB:
            # Add LED start index high and low bytes
            msg += [0, 0]

        for i in range(self.__n_leds):
            if self.__led_protocol == self.WLED_PROTOCOL_WARLS:
                msg += [i, 0, 0, 0]
            elif self.__led_protocol == self.WLED_PROTOCOL_DNRGB:
                msg += [0, 0, 0]

        print('Resetting LEDs...')
        self.__send_udp_message(msg)

    def render_led_buffer(self):
        msg = self.__create_message_header_array()

        if self.__led_protocol == WledCommunicationManager.WLED_PROTOCOL_DNRGB:
            # Add LED start index high and low bytes
            msg += [0, 0]

        for led_index in range(self.__n_leds):
            led_color_array = self.__led_manager.get_single_led_color_triple(led_index)
            if self.__led_protocol == WledCommunicationManager.WLED_PROTOCOL_WARLS:
                msg.append(led_index)
            msg += led_color_array

        # print(msg)
        self.__send_udp_message(msg)

    def connect(self):
        self.__socket = WledCommunicationManager.create_socket()
        self.__reset_leds()
