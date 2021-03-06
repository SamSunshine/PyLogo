from pygame.color import Color

import core.gui as gui
from core.gui import HOR_SEP
from core.sim_engine import SimEngine
from core.utils import rgb_to_hex
from core.world_patch_block import Patch, World

import PySimpleGUI as sg

from random import randint

from typing import Tuple


class OnOffPatch(Patch):

    # These are rgb colors
    on_color = Color('white')
    off_color = Color('black')

    def __init__(self, *args, **kw_args):
        super().__init__(*args, **kw_args)
        self.is_on = False

    def set_on_off(self, is_on: bool):
        self.is_on = is_on
        self.set_color(OnOffPatch.on_color if self.is_on else OnOffPatch.off_color)


class OnOffWorld(World):

    WHITE = '#ffffff'
    BLACK = '#000000'

    on_color_chooser = sg.ColorChooserButton('on', button_color=(WHITE, WHITE), size=(10, 1))
    off_color_chooser = sg.ColorChooserButton('off', button_color=(BLACK, BLACK), size=(10, 1))

    SELECT_ON_TEXT = 'Select "on" color  '
    SELECT_OFF_TEXT = 'Select "off" color'

    @staticmethod
    def get_color_and_update_button(button, default_color_string):
        key = button.get_text()
        color_string = SimEngine.get_gui_value(key)
        if color_string in {'None', '', None}:
            color_string = default_color_string
        button.update(button_color=(color_string, color_string))
        color = Color(color_string)
        return color

    def get_colors(self):
        OnOffPatch.off_color = self.get_color_and_update_button(
                                            self.off_color_chooser,
                                            default_color_string=rgb_to_hex(OnOffPatch.off_color))
        OnOffPatch.on_color = self.get_color_and_update_button(
                                            self.on_color_chooser,
                                            default_color_string=rgb_to_hex(OnOffPatch.on_color))

    def handle_event_and_values(self):
        """
        This method handles the color chooser. It does it in a round-about way because
        the color chooser can't generate events. Consequently, the user is asked to click
        a button next to the color-chooser. In processing that button-click, we ".click()"
        the color-chooser button. The user selects a color, which we retrieve by reading
        the window. We then color the color-chooser button with that color.
        """
        event = SimEngine.get_gui_event()
        if event not in {OnOffWorld.SELECT_ON_TEXT, OnOffWorld.SELECT_OFF_TEXT}:
            return

        selecting_on = event == OnOffWorld.SELECT_ON_TEXT
        # There are two color-choosers: selecting_on and selecting_off. Determine and select the
        # desired color chooser based on the label on the button the user clicked.
        color_chooser_button = OnOffWorld.on_color_chooser if selecting_on else OnOffWorld.off_color_chooser
        # Run it
        color_chooser_button.click()

        # Create a default color_string in case the user had cancelled color selection.
        # The default color string is the string of the current color.
        default_color_string = rgb_to_hex(OnOffPatch.on_color if selecting_on else OnOffPatch.off_color)
        # Retrieve the color choice by reading the window.
        (_event, SimEngine.values) = gui.WINDOW.read(timeout=10)

        color = self.get_color_and_update_button(color_chooser_button, default_color_string)

        # Set the color to the new choice
        if selecting_on:
            OnOffPatch.on_color = color
        else:
            OnOffPatch.off_color = color

        # Update the patches.
        for patch in self.patches:
            patch.set_on_off(patch.is_on)

    def mouse_click(self, xy: Tuple[int, int]):
        """ Toggle clicked patch's aliveness. """
        patch = self.pixel_tuple_to_patch(xy)
        patch.set_on_off(not patch.is_on)

    def setup(self):
        self.get_colors()
        for patch in self.patches:
            is_on = randint(0, 100) < 10
            patch.set_on_off(is_on)

    def step(self):
        self.get_colors()

        # Run this only if we're running this on its own.
        if isinstance(self, OnOffWorld):
            for patch in self.patches:
                is_on = patch.is_on and randint(0, 100) < 90 or not patch.is_on and randint(0, 100) < 1
                patch.set_on_off(is_on)


# ############################################## Define GUI ############################################## #
on_off_left_upper = [
                     [sg.Button(OnOffWorld.SELECT_ON_TEXT), OnOffWorld.on_color_chooser],

                     [sg.Button(OnOffWorld.SELECT_OFF_TEXT), OnOffWorld.off_color_chooser],

                     HOR_SEP(),

                     [sg.Text('Cells can be toggled when\nthe system is stopped.')],
                    ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(OnOffWorld, 'On-Off World', on_off_left_upper, patch_class=OnOffPatch, fps=10)
