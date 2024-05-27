import threading
import time

from led import LedManager
from midi import MidiManager
from wled_communication import WledCommunicationManager

class LedMidiController:

    FPS_DEFAULT = 120.0
    N_LEDS_DEFAULT = 80

    __led_manager: LedManager = None
    __midi_manager: MidiManager = None
    __wled_manager: WledCommunicationManager = None

    __lock: threading.Lock = None

    def __init__(self, led_manager: LedManager, midi_manager: MidiManager, wled_manager: WledCommunicationManager, fps: int = None) -> None:
        self.__led_manager = led_manager
        self.__midi_manager = midi_manager
        self.__wled_manager = wled_manager
        self.__fps = fps or LedMidiController.FPS_DEFAULT
        self.__seconds_per_frame = 1.0 / self.__fps

        self.__lock = threading.Lock()

    def __setup(self) -> None:
        self.__wled_manager.connect()
        self.__midi_manager.connect()

    def __render_loop(self) -> None:
        frame_number = 0
        while True:
            with self.__lock:
                self.__led_manager.update_led_buffer(frame_number)
                self.__wled_manager.render_led_buffer()
            frame_number = (frame_number + 1) % int(self.__fps)
            time.sleep(self.__seconds_per_frame)

    def run(self):
        self.__setup()
        self.__render_loop()

if __name__ == '__main__':
    midiManager = MidiManager()
    ledManager = LedManager(midiManager, LedMidiController.FPS_DEFAULT, LedMidiController.N_LEDS_DEFAULT)
    wledCommunicationManager = WledCommunicationManager(ledManager, LedMidiController.N_LEDS_DEFAULT)
    controller = LedMidiController(ledManager, midiManager, wledCommunicationManager)
    controller.run()