from midi import MidiManager

class LedManager:
    MAX_BRIGHTNESS_VALUE = 255
    COLOR_WHEEL_LENGTH = 256 * 6
    MAX_COLOR_WHEEL_INDEX = COLOR_WHEEL_LENGTH - 1

    def __init__(self, midi_manager: MidiManager, fps: float, n_leds: int) -> None:
        self.__midi_manager = midi_manager
        self.__fps = fps
        self.__n_leds = n_leds
        self.__led_buffer = [[0, 0, 0]] * self.__n_leds

    @staticmethod
    def get_color_wheel_triple(color_wheel_index):
        segment = int(color_wheel_index / (LedManager.MAX_BRIGHTNESS_VALUE + 1))
        remainder = int(color_wheel_index % (LedManager.MAX_BRIGHTNESS_VALUE + 1))

        if segment == 0:
            return [LedManager.MAX_BRIGHTNESS_VALUE, remainder, 0]
        elif segment == 1:
            return [LedManager.MAX_BRIGHTNESS_VALUE - remainder, LedManager.MAX_BRIGHTNESS_VALUE, 0]
        elif segment == 2:
            return [0, LedManager.MAX_BRIGHTNESS_VALUE, remainder]
        elif segment == 3:
            return [0, LedManager.MAX_BRIGHTNESS_VALUE - remainder, LedManager.MAX_BRIGHTNESS_VALUE]
        elif segment == 4:
            return [remainder, 0, LedManager.MAX_BRIGHTNESS_VALUE]
        elif segment == 5:
            return [LedManager.MAX_BRIGHTNESS_VALUE, 0, LedManager.MAX_BRIGHTNESS_VALUE - remainder]

    def update_led_buffer(self, frame_number: int = 0) -> None:
        frame_percent = frame_number / (self.__fps - 1.0)
        color_wheel_triple = LedManager.get_color_wheel_triple(int(self.MAX_COLOR_WHEEL_INDEX * frame_percent))
        red_cw, green_cw, blue_cw = color_wheel_triple

        for note_number in range(MidiManager.N_MIDI_NOTES):
            note_number_to_led_index_piano_normalized = note_number - MidiManager.PIANO_LOW_A_NOTE_NUMBER
            if not (0 <= note_number_to_led_index_piano_normalized < self.__n_leds):
                continue

            velocity = 0
            note_on_velocity = self.__midi_manager.try_get_note_on_velocity(note_number)
            if note_on_velocity:
                velocity = note_on_velocity
            else:
                sustained_note_velocity = self.__midi_manager.try_get_sustained_note_velocity(note_number)
                if sustained_note_velocity:
                    velocity = sustained_note_velocity

            velocity_percent = velocity / 127.0
            red = int(velocity_percent * red_cw)
            green = int(velocity_percent * green_cw)
            blue = int(velocity_percent * blue_cw)

            rgb_array = [red, green, blue]
            self.__led_buffer[note_number_to_led_index_piano_normalized] = rgb_array

    def get_single_led_color_triple(self, led_index: int) -> list[int]:
        return self.__led_buffer[led_index]

