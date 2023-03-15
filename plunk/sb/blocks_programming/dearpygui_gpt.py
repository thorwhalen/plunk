import dearpygui.dearpygui as dpg
import matplotlib.pyplot as plt


def create_plot_node(sender, data):
    # Get the input node's value
    input_node_id = dpg.get_item_parent(sender)
    input_value = dpg.get_value(input_node_id)

    # Create a figure and plot the input value
    fig, ax = plt.subplots()
    ax.plot(input_value)
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    ax.set_title("Input List")

    # Display the plot
    plt.show()


with dpg.window():
    with dpg.node_editor():
        # Create an input node
        input_node_id = dpg.add_input_text_node(
            label="Input List", data_type=dpg.mvDataType_Int_Array
        )

        # Create a view node
        view_node_id = dpg.add_view_node(label="View List")
        dpg.set_node_callback(view_node_id, create_plot_node)

        # Connect the input node to the view node
        dpg.add_node_link(input_node_id, view_node_id)

dpg.start_dearpygui()
