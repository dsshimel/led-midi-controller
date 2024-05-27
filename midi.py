import rtmidi
from typing import Optional

class MidiManager:
    # https://midi.org/expanded-midi-1-0-messages-list
    MIDI_CHANNEL_1_NOTE_OFF = 128
    MIDI_CHANNEL_1_NOTE_ON = 144
    SUSTAIN_PEDAL_YAMAHA_S90 = 176
    PIANO_LOW_A_NOTE_NUMBER = 21
    N_MIDI_NOTES = 128

    def __init__(self) -> None:
        # Key: note number; value: velocity
        self.__notes_on_buffer = {}
        self.__notes_sustained_buffer = {}
        self.__midi_cc_states = {self.SUSTAIN_PEDAL_YAMAHA_S90: False}

    def try_get_note_on_velocity(self, note_number: int) -> Optional[int]:
        return self.__notes_on_buffer.get(note_number)

    def try_get_sustained_note_velocity(self, note_number: int) -> Optional[int]:
        return self.__notes_sustained_buffer.get(note_number)

    def __on_midi_message(self, message, data=None):
        midi_msg, _ = message
        midi_event, midi_data, midi_value = midi_msg[0], midi_msg[1], midi_msg[2]

        velocity = None
        note_number = None

        if midi_event == MidiManager.MIDI_CHANNEL_1_NOTE_ON:
            note_number = midi_data
            velocity = midi_value
        elif midi_event == MidiManager.MIDI_CHANNEL_1_NOTE_OFF:
            note_number = midi_data
            velocity = 0
        elif midi_event == MidiManager.SUSTAIN_PEDAL_YAMAHA_S90:
            sustain_pedal_on = midi_value > 0
            self.__midi_cc_states[MidiManager.SUSTAIN_PEDAL_YAMAHA_S90] = sustain_pedal_on
            if sustain_pedal_on:
                self.__notes_sustained_buffer.update(self.__notes_on_buffer)
            else:
                self.__notes_sustained_buffer.clear()
            return

        if note_number is None:
            return

        if velocity == 0:
            if note_number in self.__notes_on_buffer:
                del self.__notes_on_buffer[note_number]
        else:
            self.__notes_on_buffer[note_number] = velocity
            sustain_pedal_on = self.__midi_cc_states[MidiManager.SUSTAIN_PEDAL_YAMAHA_S90]
            if sustain_pedal_on:
                self.__notes_sustained_buffer[note_number] = velocity


    def __on_midi_error(rt_midi_error_type, error_msg, data=None):
        print('MIDI error: ' + str(rt_midi_error_type))
        print('Error message: ' + error_msg)

    def connect(self) -> None:
        # Assume there's only one MIDI input device and it's on port 0
        keyboard_input = rtmidi.MidiIn()
        keyboard_input.open_port(0, 'usb-keyboard')
        keyboard_input.set_callback(self.__on_midi_message)
        keyboard_input.set_error_callback(self.__on_midi_error)