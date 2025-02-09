import dearpygui.dearpygui as dpg
from more_itertools import windowed
import numpy as np


########################################################################################################################
# Setup
########################################################################################################################
dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

########################################################################################################################
# Themes
########################################################################################################################

with dpg.theme() as _source_theme:
    with dpg.theme_component(dpg.mvButton):
        # dpg.add_theme_color(dpg.mvThemeCol_Button, [25, 119, 0])
        dpg.add_theme_color(dpg.mvThemeCol_Button, [116, 185, 255])

        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [25, 255, 0])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [25, 119, 0])

with dpg.theme() as _completion_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar, [37, 28, 138], category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered, [37, 28, 138], category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected, [37, 28, 138], category=dpg.mvThemeCat_Nodes
        )


########################################################################################################################
# Node DPG Wrappings
########################################################################################################################
class OutputNodeAttribute:
    def __init__(self, label: str = 'output'):

        self._label = label
        self.uuid = dpg.generate_uuid()
        self._children = []  # output attributes
        self._data = None

    def add_child(self, parent, child):

        dpg.add_node_link(self.uuid, child.uuid, parent=parent)
        child.set_parent(self)
        self._children.append(child)

    def execute(self, data):
        self._data = data
        for child in self._children:
            child._data = self._data

    def submit(self, parent):

        with dpg.node_attribute(
            parent=parent,
            attribute_type=dpg.mvNode_Attr_Output,
            user_data=self,
            id=self.uuid,
        ):
            dpg.add_text(self._label)


class InputNodeAttribute:
    def __init__(self, label: str = 'input'):

        self._label = label
        self.uuid = dpg.generate_uuid()
        self._parent = None  # input attribute
        self._data = None

    def get_data(self):
        return self._data

    def set_parent(self, parent: OutputNodeAttribute):
        self._parent = parent

    def submit(self, parent):

        with dpg.node_attribute(parent=parent, user_data=self, id=self.uuid):
            dpg.add_text(self._label)


class Node:
    def __init__(self, label: str, data):

        self.label = label
        self.uuid = dpg.generate_uuid()
        self.static_uuid = dpg.generate_uuid()
        self._input_attributes = []
        self._output_attributes = []
        self._data = data

    def finish(self):
        dpg.bind_item_theme(self.uuid, _completion_theme)

    def add_input_attribute(self, attribute: InputNodeAttribute):
        self._input_attributes.append(attribute)

    def add_output_attribute(self, attribute: OutputNodeAttribute):
        self._output_attributes.append(attribute)

    def execute(self):

        for attribute in self._output_attributes:
            attribute.execute(self._data)

        self.finish()

    def custom(self):
        pass

    def submit(self, parent):

        with dpg.node(parent=parent, label=self.label, tag=self.uuid):

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(
                    label='Execute',
                    user_data=self,
                    callback=lambda s, a, u: u.execute(),
                )

            for attribute in self._input_attributes:
                attribute.submit(self.uuid)

            with dpg.node_attribute(
                parent=self.uuid,
                attribute_type=dpg.mvNode_Attr_Static,
                user_data=self,
                tag=self.static_uuid,
            ):
                self.custom()

            for attribute in self._output_attributes:
                attribute.submit(self.uuid)


class NodeEditor:
    @staticmethod
    def _link_callback(sender, app_data, user_data):
        output_attr_uuid, input_attr_uuid = app_data

        input_attr = dpg.get_item_user_data(input_attr_uuid)
        output_attr = dpg.get_item_user_data(output_attr_uuid)

        output_attr.add_child(sender, input_attr)
        # self._links.append((output_attr_uuid, input_attr_uuid))
        metadata.append((output_attr_uuid, input_attr_uuid))

    def __init__(self, metadata=None):

        self._nodes = []
        # self._links = []
        self.uuid = dpg.generate_uuid()

    def add_node(self, node: Node):
        self._nodes.append(node)

    def on_drop(self, sender, app_data, user_data):
        source, generator, data = app_data
        node = generator(source.label, data)
        node.submit(self.uuid)
        self.add_node(node)

    def submit(self, parent):

        with dpg.child_window(
            width=-160,
            parent=parent,
            user_data=self,
            drop_callback=lambda s, a, u: dpg.get_item_user_data(s).on_drop(s, a, u),
        ):
            with dpg.node_editor(
                tag=self.uuid, callback=NodeEditor._link_callback, width=-1, height=-1
            ):
                for node in self._nodes:
                    node.submit(self.uuid)


########################################################################################################################
# Drag & Drop
########################################################################################################################
class DragSource:
    def __init__(self, label: str, node_generator, data):

        self.label = label
        self._generator = node_generator
        self._data = data

    def submit(self, parent):

        dpg.add_button(label=self.label, parent=parent, width=-1)
        dpg.bind_item_theme(dpg.last_item(), _source_theme)

        with dpg.drag_payload(
            parent=dpg.last_item(), drag_data=(self, self._generator, self._data)
        ):
            dpg.add_text(f'Name: {self.label}')


class DragSourceContainer:
    def __init__(self, label: str, width: int = 150, height: int = -1):

        self._label = label
        self._width = width
        self._height = height
        self._uuid = dpg.generate_uuid()
        self._children = []  # drag sources

    def add_drag_source(self, source: DragSource):

        self._children.append(source)

    def submit(self, parent):

        with dpg.child_window(
            parent=parent,
            width=self._width,
            height=self._height,
            tag=self._uuid,
            menubar=True,
        ) as child_parent:
            with dpg.menu_bar():
                dpg.add_menu(label=self._label)

            for child in self._children:
                child.submit(child_parent)


########################################################################################################################
# Inspectors
########################################################################################################################


########################################################################################################################
# Functions
########################################################################################################################


class ChunkerNode(Node):
    @staticmethod
    def factory(name, data):
        node = ChunkerNode(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_input_attribute(InputNodeAttribute('wf'))
        self.add_output_attribute(OutputNodeAttribute('chks'))
        # self.add_output_attribute(OutputNodeAttribute("y mod"))

        self.x_shift = dpg.generate_uuid()
        # self.y_shift = dpg.generate_uuid()

    def custom(self):

        dpg.add_input_int(label='chk_size', tag=self.x_shift, step=0, width=150)
        # dpg.add_input_float(label="y", tag=self.y_shift, step=0, width=150)

    def execute(self):

        # get values from static attributes
        # x_shift = dpg.get_value(self.x_shift)
        # y_shift = dpg.get_value(self.y_shift)

        # get input attribute data
        x_orig_data = self._input_attributes[0].get_data()
        # y_orig_data = self._input_attributes[1].get_data()

        # perform actual operations
        x_data = windowed(x_orig_data, 3)

        # execute output attributes
        self._output_attributes[0].execute(x_data)
        # self._output_attributes[1].execute(y_data)

        self.finish()


class FeaturizerNode(Node):
    @staticmethod
    def factory(name, data):
        node = FeaturizerNode(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_input_attribute(InputNodeAttribute('chks'))

        self.add_output_attribute(OutputNodeAttribute('fvs'))
        # self.add_output_attribute(OutputNodeAttribute("y mod"))

        self.x_shift = dpg.generate_uuid()
        # self.y_shift = dpg.generate_uuid()

    def custom(self):

        dpg.add_input_float(label='x', tag=self.x_shift, step=0, width=150)
        # dpg.add_input_float(label="y", tag=self.y_shift, step=0, width=150)

    def execute(self):

        # get values from static attributes
        # x_shift = dpg.get_value(self.x_shift)
        # y_shift = dpg.get_value(self.y_shift)

        # get input attribute data
        x_orig_data = self._input_attributes[0].get_data()
        # y_orig_data = self._input_attributes[1].get_data()

        # perform actual operations
        x_data = [np.std(x) for x in x_orig_data]

        # execute output attributes
        self._output_attributes[0].execute(x_data)
        # self._output_attributes[1].execute(y_data)

        self.finish()


########################################################################################################################
# Tools
########################################################################################################################
class ViewNode_1D(Node):
    @staticmethod
    def factory(name, data):
        node = ViewNode_1D(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_input_attribute(InputNodeAttribute('x'))
        self.simple_plot = dpg.generate_uuid()

    def custom(self):

        dpg.add_simple_plot(
            label='Data View', width=200, height=80, tag=self.simple_plot
        )

    def execute(self):

        # plot_id = self._static_attributes[0].simple_plot
        # plot_id = self._input_attributes[0].simple_plot
        dpg.set_value(self.simple_plot, self._input_attributes[0].get_data())
        self.finish()


class ViewNode_2D(Node):
    @staticmethod
    def factory(name, data):
        node = ViewNode_2D(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_input_attribute(InputNodeAttribute('x'))
        self.add_input_attribute(InputNodeAttribute('y'))

        self.x_axis = dpg.generate_uuid()
        self.y_axis = dpg.generate_uuid()

    def custom(self):

        with dpg.plot(height=400, width=400, no_title=True):
            dpg.add_plot_axis(dpg.mvXAxis, label='', tag=self.x_axis)
            dpg.add_plot_axis(dpg.mvYAxis, label='', tag=self.y_axis)

    def execute(self):

        x_axis_id = self.x_axis
        y_axis_id = self.y_axis

        x_orig_data = self._input_attributes[0].get_data()
        y_orig_data = self._input_attributes[1].get_data()

        dpg.add_line_series(x_orig_data, y_orig_data, parent=y_axis_id)
        dpg.fit_axis_data(x_axis_id)
        dpg.fit_axis_data(y_axis_id)

        self.finish()


class PlotNode_1D(Node):
    @staticmethod
    def factory(name, data):
        node = PlotNode_1D(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_input_attribute(InputNodeAttribute('y'))
        # self.add_input_attribute(InputNodeAttribute("y"))

        self.x_axis = dpg.generate_uuid()
        self.y_axis = dpg.generate_uuid()

    def custom(self):

        with dpg.plot(height=400, width=400, no_title=True):
            dpg.add_plot_axis(dpg.mvXAxis, label='', tag=self.x_axis)
            dpg.add_plot_axis(dpg.mvYAxis, label='', tag=self.y_axis)

    def execute(self):

        x_axis_id = self.x_axis
        y_axis_id = self.y_axis

        # x_orig_data = self._input_attributes[0].get_data()
        y_orig_data = self._input_attributes[0].get_data()
        print(y_orig_data)
        # x_orig_data = range(len(y_orig_data))
        x_orig_data = range(10)

        dpg.add_line_series(x_orig_data, y_orig_data, parent=y_axis_id)
        dpg.fit_axis_data(x_axis_id)
        dpg.fit_axis_data(y_axis_id)

        self.finish()


class WavFilePlotNode(Node):
    @staticmethod
    def factory(name, data):
        node = WavFilePlotNode(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_input_attribute(InputNodeAttribute('filepath'))

        self.x_axis = dpg.generate_uuid()
        self.y_axis = dpg.generate_uuid()

    def custom(self):

        # with dpg.plot(height=400, width=400, no_title=True):
        #     dpg.add_plot_axis(dpg.mvXAxis, label="", tag=self.x_axis)
        #     dpg.add_plot_axis(dpg.mvYAxis, label="", tag=self.y_axis)
        dpg.add_simple_plot(label='Data View', width=200, height=80, tag=self.x_axis)

    def execute(self):
        import soundfile as sf

        filepath_input = self._input_attributes[0].get_data()

        data, _ = sf.read(filepath_input)
        print(f'data imported: {data.shape}')
        # dpg.add_simple_plot(
        #     label="Data View", width=200, height=80, tag=self.x_axis, data=data
        # )
        dpg.set_value(self.x_axis, data)

        self.finish()


class SpectrogramPlotNode(Node):
    @staticmethod
    def factory(name, data):
        node = SpectrogramPlotNode(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_input_attribute(InputNodeAttribute('filepath'))

        self.x_axis = dpg.generate_uuid()
        self.y_axis = dpg.generate_uuid()

    def custom(self):
        pass
        # with dpg.plot(height=400, width=400, no_title=True):
        #     dpg.add_plot_axis(dpg.mvXAxis, label="", tag=self.x_axis)
        #     dpg.add_plot_axis(dpg.mvYAxis, label="", tag=self.y_axis)
        # dpg.add_simple_plot(label="Data View", width=200, height=80, tag=self.x_axis)

    def execute(self):
        import soundfile as sf
        import numpy as np
        from hear import Sound

        # from hum.utils.librosa_utils import specshow, melspectrogram, amplitude_to_db
        from librosa.feature import melspectrogram

        filepath_input = self._input_attributes[0].get_data()

        wf, sr = sf.read(filepath_input)
        s = Sound(wf, sr)
        print(wf.shape)
        # mel_kwargs = dict(
        #     {"n_fft": 2048, "hop_length": 512, "n_mels": 128},
        # )
        # S = melspectrogram(np.array(wf[:, 1]).astype(float), sr=sr, **mel_kwargs)
        # Convert to log scale (dB). We'll use the peak power as reference.
        # texture_data = amplitude_to_db(S)
        texture_data = melspectrogram(y=wf[:, 0], sr=sr)
        # texture_data = S
        # print(f"data imported: {data.shape}")
        # dpg.add_simple_plot(
        #     label="Data View", width=200, height=80, tag=self.x_axis, data=data
        # )
        with dpg.texture_registry(show=True):
            dpg.add_static_texture(
                width=200, height=80, default_value=texture_data, tag=self.x_axis
            )

        self.finish()


class ValueNode(Node):
    @staticmethod
    def factory(name, data):
        node = ValueNode(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_output_attribute(OutputNodeAttribute('Value'))

        self.value = dpg.generate_uuid()

    def custom(self):

        with dpg.group(width=150):
            dpg.add_input_text(
                label='Input Value', tag=self.value, default_value='alarm-bell.wav'
            )

    def execute(self):

        # get input attribute data
        value = dpg.get_value(self.value)
        self._output_attributes[0].execute(value)

        self.finish()


class UploaderNode(Node):
    @staticmethod
    def factory(name, data):
        node = UploaderNode(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        self.add_output_attribute(OutputNodeAttribute('Value'))

        self.value = dpg.generate_uuid()

    def custom(self):

        with dpg.group(width=150):
            # dpg.add_input_float(
            #     label="Input Value", step=0, tag=self.value, default_value=10
            # )

            def callback(sender, app_data, user_data):
                print('Sender: ', sender)
                print('App Data: ', app_data)

            with dpg.file_dialog(
                directory_selector=False,
                show=False,
                callback=callback,
                id='file_dialog_id',
                width=700,
                height=400,
            ):
                dpg.add_file_extension('.*')
                dpg.add_file_extension('', color=(150, 255, 150, 255))
                dpg.add_file_extension(
                    'Source files (*.cpp *.h *.hpp){.cpp,.h,.hpp}',
                    color=(0, 255, 255, 255),
                )
                dpg.add_file_extension(
                    '.h', color=(255, 0, 255, 255), custom_text='[header]'
                )
                dpg.add_file_extension(
                    '.py', color=(0, 255, 0, 255), custom_text='[Python]'
                )
                dpg.add_file_extension(
                    '.wav', color=(0, 177, 0, 255), custom_text='[Wav]'
                )
            dpg.add_button(
                label='File Selector', callback=lambda: dpg.show_item('file_dialog_id'),
            )

    def execute(self):

        # get input attribute data
        value = dpg.get_value(self.value)
        print(f'execute value = {value}')
        self._output_attributes[0].execute(value)

        self.finish()


########################################################################################################################
# Application
########################################################################################################################
def save_graph(node_editor):
    import pickle

    # save the state to a pickle file
    with open('my_graph.p', 'w') as f:
        pickle.dumps(node_editor._nodes, f)


def view_state(node_editor):
    nodes = node_editor._nodes
    # state = dpg.get_item_state(node_editor)
    # print(dpg.get_selected_nodes(node_editor.uuid))
    # print(dpg.get_selected_links(node_editor.uuid))

    # dpg.get
    # print(f"{state=}")

    for node in nodes:
        # print(node._label, node._data)
        print(f'{node=}, {vars(node)}')
        # print(f"Children:\n")
        # print([dir(attribute) for attribute in node._output_attributes])
        print(dir(node))
        print(f'{node._output_attributes=}')
        print(f'attribute: {dir(node._output_attributes[0])=}')


class App:
    @staticmethod
    def data_node_factory(name, data):
        node = Node(name, data)
        node.add_output_attribute(OutputNodeAttribute('data'))
        return node

    def __init__(self):

        self.data_set_container = DragSourceContainer('Data Sets', 150, -500)
        self.tool_container = DragSourceContainer('Tools', 150, -1)
        self.inspector_container = DragSourceContainer('Inspectors', 150, -500)
        self.modifier_container = DragSourceContainer('Functions', 150, -1)
        self.plugin_menu_id = dpg.generate_uuid()
        self.left_panel = dpg.generate_uuid()
        self.right_panel = dpg.generate_uuid()

        self.plugins = []

        self.add_data_set(
            'Test Data', [-5.0, -5.0, -3.0, -3.0, 0.0, 0.0, 3.0, 3.0, 5.0, 5.0]
        )
        self.add_tool('1D Data View', ViewNode_1D.factory)
        self.add_tool('2D Data View', ViewNode_2D.factory)
        # self.add_modifier("Data Shifter", DataShifterNode.factory)
        self.add_modifier('Chunker', ChunkerNode.factory)
        self.add_modifier('Featurizer', FeaturizerNode.factory)
        self.add_modifier('Plotter', PlotNode_1D.factory)
        self.add_modifier('Upload', UploaderNode.factory)
        self.add_tool('Value Tool', ValueNode.factory)
        self.add_tool('WfPlot Tool', WavFilePlotNode.factory)
        self.add_tool('Spectrogram Tool', SpectrogramPlotNode.factory)

        # PlotNode_1D

    def update(self):

        with dpg.mutex():
            dpg.delete_item(self.left_panel, children_only=True)
            self.data_set_container.submit(self.left_panel)
            self.modifier_container.submit(self.left_panel)

            dpg.delete_item(self.right_panel, children_only=True)
            self.inspector_container.submit(self.right_panel)
            self.tool_container.submit(self.right_panel)

    def add_data_set(self, label, data):
        self.data_set_container.add_drag_source(
            DragSource(label, App.data_node_factory, data)
        )

    def add_tool(self, label, factory, data=None):
        self.tool_container.add_drag_source(DragSource(label, factory, data))

    def add_inspector(self, label, factory, data=None):
        self.inspector_container.add_drag_source(DragSource(label, factory, data))

    def add_modifier(self, label, factory, data=None):
        self.modifier_container.add_drag_source(DragSource(label, factory, data))

    def add_plugin(self, name, callback):
        self.plugins.append((name, callback))

    def start(self):

        # dpg.setup_registries()
        from dearpygui_ext.themes import create_theme_imgui_light

        dpg.create_context()
        # dpg.create_viewport(title='Custom Title', width=600, height=600)

        light_theme = create_theme_imgui_light()
        dpg.bind_theme(light_theme)
        dpg.set_viewport_title('Simple Data Flow')
        dpg.show_viewport()
        node_editor = NodeEditor()

        with dpg.window() as main_window:

            with dpg.menu_bar():

                with dpg.menu(label='Operations'):

                    dpg.add_menu_item(
                        label='Reset',
                        callback=lambda: dpg.delete_item(
                            node_editor.uuid, children_only=True
                        ),
                    )
                    dpg.add_menu_item(
                        label='Save graph',
                        # callback=lambda: save_graph(node_editor),
                        callback=lambda: view_state(node_editor),
                    )

                with dpg.menu(label='Plugins'):
                    for plugin in self.plugins:
                        dpg.add_menu_item(label=plugin[0], callback=plugin[1])

            with dpg.group(horizontal=True) as group:

                # left panel
                with dpg.group(id=self.left_panel):
                    self.data_set_container.submit(self.left_panel)
                    self.modifier_container.submit(self.left_panel)

                # center panel
                node_editor.submit(group)

                # right panel
                with dpg.group(id=self.right_panel):
                    self.inspector_container.submit(self.right_panel)
                    self.tool_container.submit(self.right_panel)

        # retrieve node editor state
        view_state(node_editor)

        dpg.set_primary_window(main_window, True)
        dpg.start_dearpygui()


if __name__ == '__main__':

    app = App()
    app.start()
