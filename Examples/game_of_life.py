
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine

from random import randint


class Life_Patch(OnOffPatch):

    def __init__(self, *args, **kw_args):
        super().__init__(*args, **kw_args)
        self.live_neighbors = 0

    def is_alive(self):
        return self.is_on

    def count_live_neighbors(self):
        self.live_neighbors = sum([1 for p in self.neighbors_8() if p.is_alive()])
        
    def set_alive_or_dead(self, alive_or_dead: bool):
        self.set_on_off(alive_or_dead)


class Life_World(OnOffWorld):

    def setup(self):
        super().setup()
        density = SimEngine.get_gui_value('density')
        for patch in self.patches:
            is_alive = randint(0, 100) < density
            patch.set_alive_or_dead(is_alive)

    def step(self):
        # Count the live neighbors in the current state.
        for patch in self.patches:
            patch.count_live_neighbors()

        # Determine and set whether each patch is_alive in the next state.
        for patch in self.patches:
            is_alive = patch.live_neighbors == 3 or patch.is_alive() and patch.live_neighbors == 2
            patch.set_alive_or_dead(is_alive)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

gol_left_upper = [[sg.Text('Initial density'),
                   sg.Slider(key='density', range=(0, 80), resolution=5, size=(10, 20),
                             default_value=35, orientation='horizontal', pad=((0, 0), (0, 20)),
                             tooltip='The ratio of alive cells to all cells')]] \
                  + \
                  on_off_left_upper

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Life_World, 'Game of Life', gol_left_upper, patch_class=Life_Patch, fps=10)
