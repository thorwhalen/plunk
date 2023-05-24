from typing import Any
from functools import partial
from funcblck_io import *
from utils import IOList
import numpy as np


class FunctionBlock:
    def __init__(self, name: str):
        self.name = name

        self._event_inputs = IOList(EventInput)
        self._event_outputs = IOList(EventOutput)
        self._data_inputs = IOList(DataInput)
        self._data_outputs = IOList(DataOutput)

        self._input_mapping = []
        self._output_mapping = []

        self._states = []

        self.add_event_input('INIT')
        self.add_event_output('INITO')
        self.add_state('START')

    def __str__(self) -> str:
        return self.name

    def add_event_input(self, name: str):
        self._check_name_uniqueness(name, 'ios')
        on_event = partial(self._on_input_event, len(self._event_inputs))
        self._event_inputs.append(EventInput(name, self.name, on_event))
        self._input_mapping.append(IOList(DataInput))

    def add_event_output(self, name: str):
        self._check_name_uniqueness(name, 'ios')
        on_event = partial(self._on_output_event, len(self._event_outputs))
        self._event_outputs.append(EventOutput(name, self.name, on_event))
        self._output_mapping.append(IOList(DataOutput))

    def add_data_input(self, name: str, datatype: type):
        self._check_name_uniqueness(name, 'ios')
        self._data_inputs.append(DataInput(name, self.name, datatype))

    def add_data_output(self, name: str,  datatype: type):
        self._check_name_uniqueness(name, 'ios')
        self._data_outputs.append(DataOutput(name, self.name, datatype))

    def add_state(self, name: str) -> None:
        self._check_name_uniqueness(name, 'states')
        self._states.append(State(name))

    def map_inputs(self, event_name: str, data_name: str) -> None:
        event_ind = self._event_inputs.index_by_name(event_name)
        data_ind = self._data_inputs.index_by_name(data_name)
        self._input_mapping[event_ind].append(self._data_inputs[data_ind])

    def map_outputs(self, event_name: str, data_name: str) -> None:
        event_ind = self._event_outputs.index_by_name(event_name)
        data_ind = self._data_outputs.index_by_name(data_name)
        self._output_mapping[event_ind].append(self._data_outputs[data_ind])

    def print_ios(self):
        self._event_inputs.print_without_container()
        self._data_inputs.print_without_container()
        print('Mapping:')
        for event_ind, event in enumerate(self._event_inputs):
            print(f'\t{event.name} --> ', end='')
            self._input_mapping[event_ind].print_names_only()
        print('')
        self._event_outputs.print_without_container()
        self._data_outputs.print_without_container()
        print('Mapping')
        for event_ind, event in enumerate(self._event_outputs):
            print(f'\t{event.name} --> ', end='')
            self._output_mapping[event_ind].print_names_only()

    def _check_name_uniqueness(self, name: str, type_: str) -> None:
        if type_ == 'ios':
            obj_list = self._event_inputs + self._event_outputs + \
                self._data_inputs + self._data_outputs
        elif type_ == 'states':
            obj_list = self._states
        name_list = [obj.name for obj in obj_list]
        if name in name_list:
            raise NameError(f'{name} is already used!')
        
    def _on_input_event(self, event_ind):
        for data_input in self._input_mapping[event_ind]:
            data_input.pull_data()

    def _on_output_event(self, event_ind):
        pass


class Transition:
    def __init__(self):
        pass


class State:
    def __init__(self, name: str):
        self.name = name
        self.algos = []
        self._transitions = []

    def __str__(self) -> str:
        return self.name

    def execute(self) -> None:
        for algo in self.algos:
            algo()
        self.assess_transitions()

    def __call__(self) -> None:
        self.execute()

    def assess_transitions(self):
        pass
