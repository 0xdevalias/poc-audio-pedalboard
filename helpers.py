from pprint import pprint, pformat

from pedalboard import load_plugin, VST3Plugin, AudioUnitPlugin


def pprint_with_indent(data, indent=4):
    output = pformat(data)
    indented_output = (' ' * indent) + ('\n' + ' ' * indent).join(output.splitlines())
    print(indented_output)


# Filter the locally installed audio plugins by the provided names
#
# Example usage:
#   filter_installed_plugins_by_names(
#     ['Vital', 'Serum']
#    )
def filter_installed_plugins_by_names(filters):
    print("Showing installed VST/AU plugins, filtered by names:")

    plugins_filter = {name.lower() for name in filters}
    filtered_vst3_plugins = [
        plugin_path for plugin_path in VST3Plugin.installed_plugins
        if any(plugin_name in plugin_path.lower() for plugin_name in plugins_filter)
    ]

    filtered_au_plugins = [
        plugin_path for plugin_path in AudioUnitPlugin.installed_plugins
        if any(plugin_name in plugin_path.lower() for plugin_name in plugins_filter)
    ]

    print(f"Plugin filters: {filters}")

    print("  Filtered VST3 Plugins:")
    pprint_with_indent(filtered_vst3_plugins, indent=4)

    print("  Filtered AudioUnit Plugins:")
    pprint_with_indent(filtered_au_plugins, indent=4)


# Compare the plugin parameters between the VST3 and AudioUnit versions of a plugin, showing the differences and similarities
#
# Example usage:
#   compare_plugin_parameters(
#     "/Library/Audio/Plug-Ins/VST3/Vital.vst3",
#     "/Library/Audio/Plug-Ins/Components/Vital.component"
#   )
def compare_plugin_parameters(vst3_path, au_path):
    print("Comparing plugin parameters between VST3 and AudioUnit plugins:")
    print("  Loading VST3 plugin..")
    vst3_plugin = load_plugin(vst3_path)
    print("  Successfully loaded VST3 plugin.")

    print("  Loading AudioUnit plugin..")
    au_plugin = load_plugin(au_path)
    print("  Successfully loaded AudioUnit plugin.")

    vst3_params = set(vst3_plugin.parameters.keys())
    au_params = set(au_plugin.parameters.keys())

    only_in_vst3 = vst3_params - au_params
    only_in_au = au_params - vst3_params
    in_both = vst3_params & au_params

    print("  Parameters only in VST3:", only_in_vst3)
    print("  Parameters only in AU:", only_in_au)
    print("  Parameters in both:", in_both)


# Example usage:
# Assuming synth_plugin.parameters['verb_wet'] is your parameter:
#   verb_wet = synth_plugin.parameters['verb_wet']
#   print_parameter_properties(verb_wet)
def print_parameter_properties(parameter):
    """
    Helper function to print out properties of an AudioProcessorParameter.

    Args:
    - parameter: An instance of AudioProcessorParameter.

    See: https://github.com/spotify/pedalboard/blob/f2c2ccd64e78abaf9b87bc2c59097965c8b92fe5/pedalboard/ExternalPlugin.h#L1307-L1310
    """
    # List of property names to display
    properties = [
        'index',
        'name',
        'python_name',
        'string_value',
        'raw_value',
        'default_raw_value',
        'range',
        'max_value',
        'min_value',
        'step_size',
        'approximate_step_size',
        'num_steps',
        'type',
        'units',
        'label',
        'is_discrete',
        'is_boolean',
        'is_orientation_inverted',
        'is_automatable',
        'is_meta_parameter',
    ]

    # Iterate over the property names
    for property_name in properties:
        try:
            # Access the property value
            property_value = getattr(parameter, property_name)
            # Print the property name and its value
            pprint(f"{property_name}: {property_value}")
        except AttributeError as e:
            # If the property does not exist, print an error message
            pprint(f"{property_name}: Property does not exist. Error: {e}")
