import re
import os
import random
import string
import subprocess
from .animation import generate_animation_for_world
from .utils import compile_controllers


class Competitor:
    def __init__(self, git, rank):
        self.git = git
        self.rank = rank
        self.controller_name = self.__set_random_controller_name()

    def __set_random_controller_name(self, size=10):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return 'wb_' + ''.join(random.choice(chars) for _ in range(size))


def _get_competitors():
    # TODO: This should be retrived from forks
    return [
        Competitor(git='https://github.com/lukicdarkoo/webots-competition-participant-template', rank=1),
        Competitor(git='https://github.com/lukicdarkoo/webots-competition-participant-template', rank=2),
        Competitor(git='https://github.com/lukicdarkoo/webots-competition-participant-template', rank=3),
    ]


def _set_controller_name_to_world(world_file, robot_name, controller_name):
    world_content = None
    with open(world_file, 'r') as f:
        world_content = f.read()
    controller_expression = re.compile(rf'(DEF {robot_name}.*?controller\ \")(.*?)(\")', re.MULTILINE | re.DOTALL)
    new_world_content = re.sub(controller_expression, rf'\1{controller_name}\3', world_content)
    with open(world_file, 'w') as f:
        f.write(new_world_content)


def _clone_controllers(competitors):
    for competitor in competitors:
        controller_path = os.path.join('controllers', competitor.controller_name)

        # Clone controller content
        subprocess.check_output(['git', 'clone', competitor.git, controller_path])

        # Update controller's internal name
        python_filename = os.path.join(controller_path, 'participant_controller.py')
        if os.path.exists(python_filename):
            os.rename(python_filename, os.path.join(controller_path, f'{competitor.controller_name}.py'))


def generate_competition(competition_config):
    world_file = competition_config['world']
    all_competitors = _get_competitors()

    # Prepare controllers
    _clone_controllers(all_competitors)
    compile_controllers()

    lower_competitor_index = len(all_competitors) - 1
    while lower_competitor_index > 0:
        # Add two participants to the world
        _set_controller_name_to_world(world_file, 'R0', all_competitors[lower_competitor_index].controller_name)
        _set_controller_name_to_world(world_file, 'R1', all_competitors[lower_competitor_index - 1].controller_name)

        # Run duel
        generate_animation_for_world(world_file, 15 * 60)

        # Update ranks, check who won
        all_competitors[lower_competitor_index], all_competitors[lower_competitor_index - 1] =\
            all_competitors[lower_competitor_index - 1], all_competitors[lower_competitor_index]

        # Prepare next iteration
        lower_competitor_index -= 1
