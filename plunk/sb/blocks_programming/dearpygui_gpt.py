import dearpygui.dearpygui as dpg

dpg.create_context()


class OutputNodeAttribute:
    def __init__(self, label: str = "output"):

<<<<<<< HEAD
        self._label = label
        self.uuid = dpg.generate_uuid()
        self._children = []  # output attributes
        self._data = None
=======
    # Create a figure and plot the input value
    fig, ax = plt.subplots()
    ax.plot(input_value)
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.set_title('Input List')
>>>>>>> ead567c7c8b236b24ce0e5c83b8b5dbd9f3cef1e

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


<<<<<<< HEAD
class InputNodeAttribute:
    def __init__(self, label: str = "input"):

        self._label = label
        self.uuid = dpg.generate_uuid()
        self._parent = None  # input attribute
        self._data = None
=======
with dpg.window():
    with dpg.node_editor():
        # Create an input node
        input_node_id = dpg.add_input_text_node(
            label='Input List', data_type=dpg.mvDataType_Int_Array
        )

        # Create a view node
        view_node_id = dpg.add_view_node(label='View List')
        dpg.set_node_callback(view_node_id, create_plot_node)
>>>>>>> ead567c7c8b236b24ce0e5c83b8b5dbd9f3cef1e

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
                    label="Execute",
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

    def __init__(self):

        self._nodes = []
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


# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)


# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    dpg.delete_item(app_data)


with dpg.window(label="Tutorial", width=400, height=400):
    # node_editor = dpg.node_editor(
    #     callback=link_callback, delink_callback=delink_callback
    # )
    node_editor = NodeEditor()
    # with node_editor:
    with dpg.node(label="Node 1"):
        with dpg.node_attribute(label="Node A1"):
            dpg.add_input_float(label="F1", width=150)

        with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_input_float(label="F2", width=150)

    with dpg.node(label="Node 2"):
        with dpg.node_attribute(label="Node A3"):
            dpg.add_input_float(label="F3", width=200)

        with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_input_float(label="F4", width=200)
    print(node_editor._nodes)
dpg.create_viewport(title="Custom Title", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
