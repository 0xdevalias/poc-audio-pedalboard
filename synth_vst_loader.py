#!/usr/bin/env python3

# https://spotify.github.io/pedalboard/reference/pedalboard.html
#   https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.load_plugin
#   https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.ExternalPlugin
#     https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.AudioUnitPlugin
#     https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.VST3Plugin
#       https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.VST3Plugin.get_plugin_names_for_file
#       https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.VST3Plugin.is_instrument
#       https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.VST3Plugin.show_editor
#     https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.AudioProcessorParameter
#       A wrapper around various different parameters exposed by VST3Plugin or AudioUnitPlugin instances.
#       AudioProcessorParameter objects are rarely used directly, and usually used via their implicit interface:
#         print(my_plugin.parameters.keys())
#
# https://docs.python.org/3/library/argparse.html

import argparse
import os
from pprint import pprint, pp

from pedalboard import Pedalboard, load_plugin, VST3Plugin, AudioUnitPlugin
# from pedalboard.io import AudioFile
from mido import Message

from helpers import (
    filter_installed_plugins_by_names,
    compare_plugin_parameters,
    print_parameter_properties,
    is_vst3_xml,
    extract_vst3_xml
)


# Setting up argparse
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser(description="Load and compare synth plugins.")
parser.add_argument(
    '--synth-path',
    type=str,
    default='/Library/Audio/Plug-Ins/VST3/Vital.vst3',
    # default='/Library/Audio/Plug-Ins/Components/Serum.component',
    help="Path to the synth plugin file. [Default: %(default)s]",
)
parser.add_argument(
    '--enumerate-plugins',
    type=str2bool,
    nargs='?',
    const=True,  # If arg passed with no value, treat it as True
    default=True,
    choices=[True, False],
    help="Enumerate and display synth plugins. [Default: %(default)s]"
)
parser.add_argument(
    '--enumerate-params',
    type=str2bool,
    nargs='?',
    const=True,  # If arg passed with no value, treat it as True
    default=True,
    choices=[True, False],
    help="Enumerate and display synth parameters. [Default: %(default)s]"
)
parser.add_argument(
    '--output-state',
    type=str2bool,
    nargs='?',
    const=True,  # If arg passed with no value, treat it as True
    default=False,
    choices=[True, False],
    help="Output the state of the synth. [Default: %(default)s]"
)
parser.add_argument(
    '--out-state-file-initial',
    type=str,
    default='synth_raw_state_initial.bin',
    help="Filename to save the initial raw state. [Default: %(default)s]"
)
parser.add_argument(
    '--out-state-file-new',
    type=str,
    default='synth_raw_state_new.bin',
    help="Filename to save the new raw state. [Default: %(default)s]"
)
parser.add_argument(
    '--out-state-file-initial-xml',
    type=str,
    default='synth_raw_state_initial.xml',
    help="Filename to save the initial raw state XML part. [Default: %(default)s]"
)
parser.add_argument(
    '--out-state-file-new-xml',
    type=str,
    default='synth_raw_state_new.xml',
    help="Filename to save the new raw state XML part. [Default: %(default)s]"
)
parser.add_argument(
    '--force',
    type=str2bool,
    nargs='?',
    const=True,  # If arg passed with no value, treat it as True
    default=False,
    choices=[True, False],
    help="Force overwrite of existing files. [Default: %(default)s]"
)
args = parser.parse_args()

print("Args:")
for key, value in vars(args).items():
    print(f"  {key}: {value},")
print()

if args.output_state:
    # Check if the output files already exist. Warn if --force is specified, otherwise raise an error.
    existing_files = [
        f for f in [
            args.out_state_file_initial,
            args.out_state_file_initial_xml,
            args.out_state_file_new,
            args.out_state_file_new_xml
        ]
        if os.path.exists(f)
    ]
    if existing_files:
        if args.force:
            print(f"Warning: The following files will be overwritten due to --force: {', '.join(existing_files)}")
        else:
            raise FileExistsError(
                f"The following files already exist: {', '.join(existing_files)}. Use --force to overwrite."
            )

if args.enumerate_plugins:
    # Filter the locally installed audio plugins by the provided names
    filter_installed_plugins_by_names(
        ['Vital', 'Serum']
    )

    # eg.
    #   Vital
    #     VST2: /Library/Audio/Plug-Ins/VST/Vital.vst
    #     VST3: /Library/Audio/Plug-Ins/VST3/Vital.vst3
    #     AU:   /Library/Audio/Plug-Ins/Components/Vital.component
    #
    #   Serum
    #     VST2: /Library/Audio/Plug-Ins/VST/Serum.vst
    #     AU:   /Library/Audio/Plug-Ins/Components/Serum.component

# Compare the plugin parameters between the VST3 and AudioUnit versions of a plugin, showing the differences and similarities
# compare_plugin_parameters(
#   "/Library/Audio/Plug-Ins/VST3/Vital.vst3",
#   "/Library/Audio/Plug-Ins/Components/Vital.component"
# )

print(f"Loading synth plugin ({args.synth_path})..")
synth_plugin = load_plugin(args.synth_path)
print(f"  Synth plugin loaded: {synth_plugin.name}")
print(f"  Synth plugin is instrument? {synth_plugin.is_instrument}")
print(f"  Synth plugin is effect? {synth_plugin.is_effect}")
# assert synth_plugin.is_instrument

# # TODO: remove this hacky code
# pprint(dir(synth_plugin))
# pprint(synth_plugin._parameters)

# # TODO: remove this hacky code
# first_synth_param = synth_plugin.parameters[list(synth_plugin.parameters.keys())[0]]
# # pprint(dir(first_synth_param))
# print_parameter_properties(first_synth_param)
# # print_parameter_properties(synth_plugin.parameters['verb_wet'])

# print("Synth plugin parameters:")
# pprint(synth_plugin.parameters)

if args.output_state:
    print("Capturing initial raw state of the synth..")
    initial_synth_raw_state = synth_plugin.raw_state

if args.enumerate_params:
    print("Capturing initial state of synth params..")
    initial_synth_params = {key: synth_plugin.parameters[key].raw_value for key in synth_plugin.parameters.keys()}

print("Showing synth GUI..")
synth_plugin.show_editor()

if args.enumerate_params:
    print("Capturing state of synth params after showing GUI..")
    new_synth_params = {key: synth_plugin.parameters[key].raw_value for key in synth_plugin.parameters.keys()}

    # Calculate the differences
    synth_param_diffs = {
        key: {'before': initial_synth_params[key], 'after': new_synth_params[key]}
        for key in initial_synth_params
        if key in new_synth_params and initial_synth_params[key] != new_synth_params[key]
    }

    # Check for keys that exist only in one of the dictionaries
    missing_in_new = {key for key in initial_synth_params if key not in new_synth_params}
    missing_in_initial = {key for key in new_synth_params if key not in initial_synth_params}

    # Output warnings for missing keys
    if missing_in_new:
        print(
            "Warning: These keys were in the initial parameters, but are missing in the new parameters:",
            missing_in_new
        )
    if missing_in_initial:
        print(
            "Warning: These keys were not in the initial parameters, but are in the new parameters:",
            missing_in_initial
        )

    # Print out the differences
    print(f"Number of parameters before: {len(initial_synth_params)}")
    print(f"Number of parameters after: {len(new_synth_params)}")
    print(f"Number of parameters changed: {len(synth_param_diffs)}")
    for key, value in synth_param_diffs.items():
        print(
            f"Parameter: {key} ({synth_plugin.parameters[key].name}), Before: {value['before']}, After: {value['after']}")

if args.output_state:
    print("Capturing new raw state of the synth after showing GUI..")
    new_synth_raw_state = synth_plugin.raw_state

    # Output details about the raw synth state
    print(f"Raw synth state length before: {len(initial_synth_raw_state)}")
    print(f"Raw synth state length after: {len(new_synth_raw_state)}")
    # TODO: calculate the diff between initial_synth_raw_state and new_synth_raw_state?

    # Write the initial and new raw states to files
    with open(args.out_state_file_initial, 'wb') as f:
        f.write(initial_synth_raw_state)
        print(f"Initial raw state written to {args.out_state_file_initial}")

    with open(args.out_state_file_new, 'wb') as f:
        f.write(new_synth_raw_state)
        print(f"New raw state written to {args.out_state_file_new}")

    # Check and extract XML from initial state
    if is_vst3_xml(initial_synth_raw_state):
        initial_synth_state_xml = extract_vst3_xml(initial_synth_raw_state)
        with open(args.out_state_file_initial_xml, 'w') as f:
            f.write(initial_synth_state_xml)
            print(f"Initial raw state XML written to {args.out_state_file_initial_xml}")
    else:
        print("Initial state does not look like VST3 XML.")

    # Check and extract XML from new state
    if is_vst3_xml(new_synth_raw_state):
        new_synth_state_xml = extract_vst3_xml(new_synth_raw_state)
        with open(args.out_state_file_new_xml, 'w') as f:
            f.write(new_synth_state_xml)
            print(f"New raw state XML written to {args.out_state_file_new_xml}")
    else:
        print("New state does not look like VST3 XML.")

# TODO: see json serialisation for parameters stuff here:
#   save as json (basic): https://github.com/spotify/pedalboard/issues/187#issuecomment-1375662525
#   save as json (more robust): https://github.com/spotify/pedalboard/issues/187#issuecomment-1376205304
#   load from json: https://github.com/spotify/pedalboard/issues/187#issuecomment-1692655527


# sample_rate = 44100
# num_channels = 2  # Stereo output

# # Render some audio by passing MIDI to Vital:
# midi_messages = [Message("note_on", note=60), Message("note_off", note=60, time=1)]
# audio = vital_synth(midi_messages, duration=1, sample_rate=sample_rate, num_channels=num_channels)

# # Write the rendered audio to a file
# with AudioFile("output-vital-audio.wav", "w", sample_rate, num_channels) as f:
#     f.write(audio)

# Print out the parameter keys supported by the synth plugin
# print(synth_plugin.parameters.keys())
# print(len(synth_plugin.parameters.keys()))

# Serum
#   dict_keys(['mastervol', 'a_vol', 'a_pan', 'a_octave', 'a_semi', 'a_fine', 'a_unison', 'a_unidet', 'a_uniblend', 'a_warp', 'a_coarsepit', 'a_wtpos', 'a_randphase', 'a_phase', 'b_vol', 'b_pan', 'b_octave', 'b_semi', 'b_fine', 'b_unison', 'b_unidet', 'b_uniblend', 'b_warp', 'b_coarsepit', 'b_wtpos', 'b_randphase', 'b_phase', 'noise_level', 'noise_pitch', 'noise_fine', 'noise_pan', 'noise_randphase', 'noise_phase', 'sub_osc_level', 'sub_osc_pan', 'env1_atk', 'env1_hold', 'env1_dec', 'env1_sus', 'env1_rel', 'osca_fil', 'oscb_fil', 'oscn_fil', 'oscs_fil', 'fil_type', 'fil_cutoff', 'fil_reso', 'fil_driv', 'fil_var', 'fil_mix', 'fil_stereo', 'env2_atk', 'env2_hld', 'env2_dec', 'env2_sus', 'env2_rel', 'env3_atk', 'env3_hld', 'env3_dec', 'env3_sus', 'env3_rel', 'lfo1rate', 'lfo2rate', 'lfo3rate', 'lfo4rate', 'porttime', 'portcurve', 'chaos1_bpm', 'chaos2_bpm', 'chaos1_rate', 'chaos2_rate', 'a_curve1', 'd_curve1', 'r_curve1', 'a_curve2', 'd_curve2', 'r_curve2', 'a_curve3', 'd_curve3', 'r_curve3', 'verb_wet', 'verbsize', 'verbpdly', 'verbloct', 'verbdamp', 'verbhict', 'verbwdth', 'eq_frql', 'eq_frqh', 'eq_q_l', 'eq_q_h', 'eq_voll', 'eq_volh', 'eq_typl', 'eq_typh', 'dist_wet', 'dist_drv', 'dist_l_b_h', 'dist_mode', 'dist_freq', 'dist_bw', 'dist_prepost', 'flg_wet', 'flg_bpm_sync', 'flg_rate', 'flg_dep', 'flg_feed', 'flg_stereo', 'phs_wet', 'phs_bpm_sync', 'phs_rate', 'phs_dpth', 'phs_frq', 'phs_feed', 'phs_stereo', 'cho_wet', 'cho_bpm_sync', 'cho_rate', 'cho_dly', 'cho_dly2', 'cho_dep', 'cho_feed', 'cho_filt', 'dly_wet', 'dly_freq', 'dly_bw', 'dly_bpm_sync', 'dly_link', 'dly_timl', 'dly_timr', 'dly_mode', 'dly_feed', 'dly_off_l', 'dly_off_r', 'cmp_thr', 'cmp_rat', 'cmp_att', 'cmp_rel', 'cmpgain', 'cmpmbnd', 'fx_fil_wet', 'fx_fil_type', 'fx_fil_freq', 'fx_fil_reso', 'fx_fil_drive', 'fx_fil_var', 'hyp_wet', 'hyp_rate', 'hyp_detune', 'hyp_unison', 'hyp_retrig', 'hypdim_size', 'hypdim_mix', 'dist_enable', 'flg_enable', 'phs_enable', 'cho_enable', 'dly_enable', 'comp_enable', 'rev_enable', 'eq_enable', 'fx_fil_enable', 'hyp_enable', 'oscapitchtrack', 'oscbpitchtrack', 'bend_u', 'bend_d', 'warposca', 'warposcb', 'suboscshape', 'suboscoctave', 'a_uni_lr', 'b_uni_lr', 'a_uni_warp', 'b_uni_warp', 'a_uni_wtpos', 'b_uni_wtpos', 'a_uni_stack', 'b_uni_stack', 'mod_1_amt', 'mod_1_out', 'mod_2_amt', 'mod_2_out', 'mod_3_amt', 'mod_3_out', 'mod_4_amt', 'mod_4_out', 'mod_5_amt', 'mod_5_out', 'mod_6_amt', 'mod_6_out', 'mod_7_amt', 'mod_8_out', 'mod_8_amt', 'mod_9_amt', 'mod_9_out', 'mod10_amt', 'mod10_out', 'mod11_amt', 'mod11_out', 'mod12_amt', 'mod12_out', 'mod13_amt', 'mod13_out', 'mod14_amt', 'mod14_out', 'mod15_amt', 'mod15_out', 'mod16_amt', 'mod16_out', 'osc_a_on', 'osc_b_on', 'osc_n_on', 'osc_s_on', 'filter_on', 'mod_wheel', 'macro_1', 'macro_2', 'macro_3', 'macro_4', 'amp', 'lfo1_smooth', 'lfo2_smooth', 'lfo3_smooth', 'lfo4_smooth', 'pitch_bend', 'mod17_amt', 'mod17_out', 'mod18_amt', 'mod18_out', 'mod19_amt', 'mod19_out', 'mod20_amt', 'mod20_out', 'mod21_amt', 'mod21_out', 'mod22_amt', 'mod22_out', 'mod23_amt', 'mod23_out', 'mod24_amt', 'mod24_out', 'mod25_amt', 'mod25_out', 'mod26_amt', 'mod26_out', 'mod27_amt', 'mod27_out', 'mod28_amt', 'mod28_out', 'mod29_amt', 'mod29_out', 'mod30_amt', 'mod30_out', 'mod31_amt', 'mod31_out', 'mod32_amt', 'mod32_out', 'lfo5rate', 'lfo6rate', 'lfo7rate', 'lfo8rate', 'lfo5_smooth', 'lfo6_smooth', 'lfo7_smooth', 'lfo8_smooth', 'fxfil_pan', 'comp_wet', 'gain_l', 'gain_m', 'gain_h', 'lfo1_rise', 'lfo2_rise', 'lfo3_rise', 'lfo4_rise', 'lfo5_rise', 'lfo6_rise', 'lfo7_rise', 'lfo8_rise', 'lfo1_delay', 'lfo2_delay', 'lfo3_delay', 'lfo4_delay', 'lfo5_delay', 'lfo6_delay', 'lfo7_delay', 'lfo8_delay'])

# Vital
#   dict_keys(['beats_per_minute', 'chorus_filter_cutoff', 'chorus_delay_1', 'chorus_delay_2', 'chorus_mix', 'chorus_feedback', 'chorus_frequency', 'chorus_mod_depth', 'chorus_switch', 'chorus_sync', 'chorus_tempo', 'compressor_attack', 'compressor_band_gain', 'band_lower_ratio', 'band_lower_threshold', 'band_upper_ratio', 'band_upper_threshold', 'compressor_enabled_bands', 'compressor_high_gain', 'high_lower_ratio', 'high_lower_threshold', 'high_upper_ratio', 'high_upper_threshold', 'compressor_low_gain', 'low_lower_ratio', 'low_lower_threshold', 'low_upper_ratio', 'low_upper_threshold', 'compressor_switch', 'compressor_release', 'delay_mix', 'delay_feedback', 'delay_filter_cutoff', 'delay_filter_spread', 'delay_frequency', 'delay_switch', 'delay_style', 'delay_sync', 'delay_tempo', 'distortion_drive', 'distortion_filter_blend', 'distortion_filter_cutoff', 'distortion_filter_order', 'distortion_filter_resonance', 'distortion_mix', 'distortion_switch', 'distortion_type', 'effect_chain_order', 'envelope_1_attack', 'envelope_1_attack_power', 'envelope_1_decay', 'envelope_1_decay_power', 'envelope_1_release', 'envelope_1_release_power', 'envelope_1_sustain', 'envelope_2_attack', 'envelope_2_attack_power', 'envelope_2_decay', 'envelope_2_decay_power', 'envelope_2_release', 'envelope_2_release_power', 'envelope_2_sustain', 'envelope_3_attack', 'envelope_3_attack_power', 'envelope_3_decay', 'envelope_3_decay_power', 'envelope_3_release', 'envelope_3_release_power', 'envelope_3_sustain', 'envelope_4_attack', 'envelope_4_attack_power', 'envelope_4_decay', 'envelope_4_decay_power', 'envelope_4_release', 'envelope_4_release_power', 'envelope_4_sustain', 'envelope_5_attack', 'envelope_5_attack_power', 'envelope_5_decay', 'envelope_5_decay_power', 'envelope_5_release', 'envelope_5_release_power', 'envelope_5_sustain', 'envelope_6_attack', 'envelope_6_attack_power', 'envelope_6_decay', 'envelope_6_decay_power', 'envelope_6_release', 'envelope_6_release_power', 'envelope_6_sustain', 'eq_band_cutoff', 'eq_band_gain', 'eq_band_resonance', 'eq_high_cutoff', 'eq_high_gain', 'eq_high_mode', 'eq_high_resonance', 'eq_low_cutoff', 'eq_low_gain', 'eq_low_mode', 'eq_low_resonance', 'eq_switch', 'filter_1_blend', 'filter_1_comb_blend_offset', 'filter_1_cutoff', 'filter_1_drive', 'filter_1_filter_input', 'filter_1_formant_resonance', 'filter_1_formant_transpose', 'filter_1_formant_x', 'filter_1_formant_y', 'filter_1_key_track', 'filter_1_mix', 'filter_1_model', 'filter_1_switch', 'filter_1_resonance', 'filter_1_style', 'filter_2_blend', 'filter_2_comb_blend_offset', 'filter_2_cutoff', 'filter_2_drive', 'filter_2_filter_input', 'filter_2_formant_resonance', 'filter_2_formant_transpose', 'filter_2_formant_x', 'filter_2_formant_y', 'filter_2_key_track', 'filter_2_mix', 'filter_2_model', 'filter_2_switch', 'filter_2_resonance', 'filter_2_style', 'filter_fx_blend', 'filter_fx_comb_blend_offset', 'filter_fx_cutoff', 'filter_fx_drive', 'filter_fx_formant_resonance', 'filter_fx_formant_transpose', 'filter_fx_formant_x', 'filter_fx_formant_y', 'filter_fx_key_track', 'filter_fx_mix', 'filter_fx_model', 'filter_fx_switch', 'filter_fx_resonance', 'filter_fx_style', 'flanger_mix', 'flanger_feedback', 'flanger_frequency', 'flanger_mod_depth', 'flanger_switch', 'flanger_phase_offset', 'flanger_sync', 'flanger_tempo', 'legato', 'lfo_1_delay', 'lfo_1_fade_in', 'lfo_1_frequency', 'lfo_1_phase', 'lfo_1_sync', 'lfo_1_sync_type', 'lfo_1_tempo', 'lfo_2_delay', 'lfo_2_fade_in', 'lfo_2_frequency', 'lfo_2_phase', 'lfo_2_sync', 'lfo_2_sync_type', 'lfo_2_tempo', 'lfo_3_delay', 'lfo_3_fade_in', 'lfo_3_frequency', 'lfo_3_phase', 'lfo_3_sync', 'lfo_3_sync_type',
#              'lfo_3_tempo', 'lfo_4_delay', 'lfo_4_fade_in', 'lfo_4_frequency', 'lfo_4_phase', 'lfo_4_sync', 'lfo_4_sync_type', 'lfo_4_tempo', 'lfo_5_delay', 'lfo_5_fade_in', 'lfo_5_frequency', 'lfo_5_phase', 'lfo_5_sync', 'lfo_5_sync_type', 'lfo_5_tempo', 'lfo_6_delay', 'lfo_6_fade_in', 'lfo_6_frequency', 'lfo_6_phase', 'lfo_6_sync', 'lfo_6_sync_type', 'lfo_6_tempo', 'lfo_7_delay', 'lfo_7_fade_in', 'lfo_7_frequency', 'lfo_7_phase', 'lfo_7_sync', 'lfo_7_sync_type', 'lfo_7_tempo', 'lfo_8_delay', 'lfo_8_fade_in', 'lfo_8_frequency', 'lfo_8_phase', 'lfo_8_sync', 'lfo_8_sync_type', 'lfo_8_tempo', 'macro_1', 'macro_2', 'macro_3', 'macro_4', 'modulation_10_amount', 'modulation_10_bipolar', 'modulation_10_bypass', 'modulation_10_power', 'modulation_10_stereo', 'modulation_11_amount', 'modulation_11_bipolar', 'modulation_11_bypass', 'modulation_11_power', 'modulation_11_stereo', 'modulation_12_amount', 'modulation_12_bipolar', 'modulation_12_bypass', 'modulation_12_power', 'modulation_12_stereo', 'modulation_13_amount', 'modulation_13_bipolar', 'modulation_13_bypass', 'modulation_13_power', 'modulation_13_stereo', 'modulation_14_amount', 'modulation_14_bipolar', 'modulation_14_bypass', 'modulation_14_power', 'modulation_14_stereo', 'modulation_15_amount', 'modulation_15_bipolar', 'modulation_15_bypass', 'modulation_15_power', 'modulation_15_stereo', 'modulation_16_amount', 'modulation_16_bipolar', 'modulation_16_bypass', 'modulation_16_power', 'modulation_16_stereo', 'modulation_17_amount', 'modulation_17_bipolar', 'modulation_17_bypass', 'modulation_17_power', 'modulation_17_stereo', 'modulation_18_amount', 'modulation_18_bipolar', 'modulation_18_bypass', 'modulation_18_power', 'modulation_18_stereo', 'modulation_19_amount', 'modulation_19_bipolar', 'modulation_19_bypass', 'modulation_19_power', 'modulation_19_stereo', 'modulation_1_amount', 'modulation_1_bipolar', 'modulation_1_bypass', 'modulation_1_power', 'modulation_1_stereo', 'modulation_20_amount', 'modulation_20_bipolar', 'modulation_20_bypass', 'modulation_20_power', 'modulation_20_stereo', 'modulation_21_amount', 'modulation_21_bipolar', 'modulation_21_bypass', 'modulation_21_power', 'modulation_21_stereo', 'modulation_22_amount', 'modulation_22_bipolar', 'modulation_22_bypass', 'modulation_22_power', 'modulation_22_stereo', 'modulation_23_amount', 'modulation_23_bipolar', 'modulation_23_bypass', 'modulation_23_power', 'modulation_23_stereo', 'modulation_24_amount', 'modulation_24_bipolar', 'modulation_24_bypass', 'modulation_24_power', 'modulation_24_stereo', 'modulation_25_amount', 'modulation_25_bipolar', 'modulation_25_bypass', 'modulation_25_power', 'modulation_25_stereo', 'modulation_26_amount', 'modulation_26_bipolar', 'modulation_26_bypass', 'modulation_26_power', 'modulation_26_stereo', 'modulation_27_amount', 'modulation_27_bipolar', 'modulation_27_bypass', 'modulation_27_power', 'modulation_27_stereo', 'modulation_28_amount', 'modulation_28_bipolar', 'modulation_28_bypass', 'modulation_28_power', 'modulation_28_stereo', 'modulation_29_amount', 'modulation_29_bipolar', 'modulation_29_bypass', 'modulation_29_power', 'modulation_29_stereo', 'modulation_2_amount', 'modulation_2_bipolar', 'modulation_2_bypass', 'modulation_2_power', 'modulation_2_stereo', 'modulation_30_amount', 'modulation_30_bipolar', 'modulation_30_bypass', 'modulation_30_power', 'modulation_30_stereo', 'modulation_31_amount', 'modulation_31_bipolar', 'modulation_31_bypass', 'modulation_31_power', 'modulation_31_stereo', 'modulation_32_amount', 'modulation_32_bipolar', 'modulation_32_bypass', 'modulation_32_power', 'modulation_32_stereo', 'modulation_3_amount', 'modulation_3_bipolar', 'modulation_3_bypass', 'modulation_3_power', 'modulation_3_stereo', 'modulation_4_amount', 'modulation_4_bipolar', 'modulation_4_bypass', 'modulation_4_power', 'modulation_4_stereo', 'modulation_5_amount', 'modulation_5_bipolar', 'modulation_5_bypass', 'modulation_5_power', 'modulation_5_stereo', 'modulation_6_amount', 'modulation_6_bipolar', 'modulation_6_bypass', 'modulation_6_power', 'modulation_6_stereo', 'modulation_7_amount', 'modulation_7_bipolar', 'modulation_7_bypass', 'modulation_7_power', 'modulation_7_stereo', 'modulation_8_amount', 'modulation_8_bipolar', 'modulation_8_bypass', 'modulation_8_power', 'modulation_8_stereo', 'modulation_9_amount', 'modulation_9_bipolar', 'modulation_9_bypass', 'modulation_9_power', 'modulation_9_stereo', 'oscillator_1_detune_power', 'oscillator_1_detune_range', 'oscillator_1_distortion_amount', 'oscillator_1_distortion_phase', 'oscillator_1_distortion_spread', 'oscillator_1_distortion_type', 'oscillator_1_unison_frame_spread', 'oscillator_1_level', 'oscillator_1_midi_track', 'oscillator_1_switch', 'oscillator_1_pan', 'oscillator_1_phase', 'oscillator_1_phase_randomization', 'oscillator_1_smooth_interpolation', 'oscillator_1_stack_style', 'oscillator_1_stereo_spread', 'oscillator_1_transpose', 'oscillator_1_transpose_quantize', 'oscillator_1_tune', 'oscillator_1_blend', 'oscillator_1_unison_detune', 'oscillator_1_unison_voices', 'oscillator_1_wave_frame', 'oscillator_2_detune_power', 'oscillator_2_detune_range', 'oscillator_2_distortion_amount', 'oscillator_2_distortion_phase', 'oscillator_2_distortion_spread', 'oscillator_2_distortion_type', 'oscillator_2_unison_frame_spread', 'oscillator_2_level', 'oscillator_2_midi_track', 'oscillator_2_switch', 'oscillator_2_pan', 'oscillator_2_phase', 'oscillator_2_phase_randomization', 'oscillator_2_smooth_interpolation', 'oscillator_2_stack_style', 'oscillator_2_stereo_spread', 'oscillator_2_transpose', 'oscillator_2_transpose_quantize', 'oscillator_2_tune', 'oscillator_2_blend', 'oscillator_2_unison_detune', 'oscillator_2_unison_voices', 'oscillator_2_wave_frame', 'oversampling', 'phaser_center', 'phaser_mix', 'phaser_feedback', 'phaser_frequency', 'phaser_mod_depth', 'phaser_switch', 'phaser_phase_offset', 'phaser_sync', 'phaser_tempo', 'pitch_bend_range', 'polyphony', 'portamento_force', 'portamento_scale', 'portamento_slope', 'portamento_time', 'reverb_chorus_amount', 'reverb_chorus_frequency', 'reverb_decay_time', 'reverb_mix', 'reverb_high_cutoff', 'reverb_high_gain', 'reverb_low_cutoff', 'reverb_low_gain', 'reverb_switch', 'reverb_pre_high_cutoff', 'reverb_pre_low_cutoff', 'sample_keytrack', 'sample_level', 'sample_loop', 'sample_switch', 'sample_pan', 'sample_random_phase', 'sample_transpose', 'sample_transpose_quantize', 'sample_tune', 'stereo_routing', 'velocity_track', 'voice_amplitude', 'voice_priority', 'voice_tune', 'volume', 'mod_wheel', 'pitch_wheel', 'random_lfo_1_frequency', 'random_lfo_1_stereo', 'random_lfo_1_style', 'random_lfo_1_sync', 'random_lfo_1_tempo', 'random_lfo_2_frequency', 'random_lfo_2_stereo', 'random_lfo_2_style', 'random_lfo_2_sync', 'random_lfo_2_tempo', 'random_lfo_3_frequency', 'random_lfo_3_stereo', 'random_lfo_3_style', 'random_lfo_3_sync', 'random_lfo_3_tempo', 'random_lfo_4_frequency', 'random_lfo_4_stereo', 'random_lfo_4_style', 'random_lfo_4_sync', 'random_lfo_4_tempo', 'oscillator_1_view_2d', 'oscillator_2_view_2d', 'lfo_1_stereo', 'lfo_2_stereo', 'lfo_3_stereo', 'lfo_4_stereo', 'lfo_5_stereo', 'lfo_6_stereo', 'lfo_7_stereo', 'lfo_8_stereo', 'oscillator_1_frequency_morph_amount', 'oscillator_1_frequency_morph_spread', 'oscillator_1_frequency_morph_type', 'oscillator_2_frequency_morph_amount', 'oscillator_2_frequency_morph_spread', 'oscillator_2_frequency_morph_type', 'oscillator_1_destination', 'oscillator_1_spectral_unison', 'oscillator_2_destination', 'oscillator_2_spectral_unison', 'oscillator_3_destination', 'oscillator_3_detune_power', 'oscillator_3_detune_range', 'oscillator_3_distortion_amount', 'oscillator_3_distortion_phase', 'oscillator_3_distortion_spread', 'oscillator_3_distortion_type', 'oscillator_3_unison_frame_spread', 'oscillator_3_level', 'oscillator_3_midi_track', 'oscillator_3_switch', 'oscillator_3_pan', 'oscillator_3_phase', 'oscillator_3_phase_randomization', 'oscillator_3_smooth_interpolation', 'oscillator_3_frequency_morph_amount', 'oscillator_3_frequency_morph_spread', 'oscillator_3_frequency_morph_type', 'oscillator_3_spectral_unison', 'oscillator_3_stack_style', 'oscillator_3_stereo_spread', 'oscillator_3_transpose', 'oscillator_3_transpose_quantize', 'oscillator_3_tune', 'oscillator_3_blend', 'oscillator_3_unison_detune', 'oscillator_3_unison_voices', 'oscillator_3_view_2d', 'oscillator_3_wave_frame', 'sample_destination', 'mpe_enabled', 'envelope_1_delay', 'envelope_2_delay', 'envelope_3_delay', 'envelope_4_delay', 'envelope_5_delay', 'envelope_6_delay', 'envelope_1_hold', 'envelope_2_hold', 'envelope_3_hold', 'envelope_4_hold', 'envelope_5_hold', 'envelope_6_hold', 'flanger_center', 'eq_band_mode', 'reverb_size', 'delay_frequency_2', 'delay_sync_2', 'delay_tempo_2', 'chorus_voices', 'phaser_blend', 'random_lfo_1_sync_type', 'random_lfo_2_sync_type', 'random_lfo_3_sync_type', 'random_lfo_4_sync_type', 'modulation_33_amount', 'modulation_33_bipolar', 'modulation_33_bypass', 'modulation_33_power', 'modulation_33_stereo', 'modulation_34_amount', 'modulation_34_bipolar', 'modulation_34_bypass', 'modulation_34_power', 'modulation_34_stereo', 'modulation_35_amount', 'modulation_35_bipolar', 'modulation_35_bypass', 'modulation_35_power', 'modulation_35_stereo', 'modulation_36_amount', 'modulation_36_bipolar', 'modulation_36_bypass', 'modulation_36_power', 'modulation_36_stereo', 'modulation_37_amount', 'modulation_37_bipolar', 'modulation_37_bypass', 'modulation_37_power', 'modulation_37_stereo', 'modulation_38_amount', 'modulation_38_bipolar', 'modulation_38_bypass', 'modulation_38_power', 'modulation_38_stereo', 'modulation_39_amount', 'modulation_39_bipolar', 'modulation_39_bypass', 'modulation_39_power', 'modulation_39_stereo', 'modulation_40_amount', 'modulation_40_bipolar', 'modulation_40_bypass', 'modulation_40_power', 'modulation_40_stereo', 'modulation_41_amount', 'modulation_41_bipolar', 'modulation_41_bypass', 'modulation_41_power', 'modulation_41_stereo', 'modulation_42_amount', 'modulation_42_bipolar', 'modulation_42_bypass', 'modulation_42_power', 'modulation_42_stereo', 'modulation_43_amount', 'modulation_43_bipolar', 'modulation_43_bypass', 'modulation_43_power', 'modulation_43_stereo', 'modulation_44_amount', 'modulation_44_bipolar', 'modulation_44_bypass', 'modulation_44_power', 'modulation_44_stereo', 'modulation_45_amount', 'modulation_45_bipolar', 'modulation_45_bypass', 'modulation_45_power', 'modulation_45_stereo', 'modulation_46_amount', 'modulation_46_bipolar', 'modulation_46_bypass', 'modulation_46_power', 'modulation_46_stereo', 'modulation_47_amount', 'modulation_47_bipolar', 'modulation_47_bypass', 'modulation_47_power', 'modulation_47_stereo', 'modulation_48_amount', 'modulation_48_bipolar', 'modulation_48_bypass', 'modulation_48_power', 'modulation_48_stereo', 'modulation_49_amount', 'modulation_49_bipolar', 'modulation_49_bypass', 'modulation_49_power', 'modulation_49_stereo', 'modulation_50_amount', 'modulation_50_bipolar', 'modulation_50_bypass', 'modulation_50_power', 'modulation_50_stereo', 'modulation_51_amount', 'modulation_51_bipolar', 'modulation_51_bypass', 'modulation_51_power', 'modulation_51_stereo', 'modulation_52_amount', 'modulation_52_bipolar', 'modulation_52_bypass', 'modulation_52_power', 'modulation_52_stereo', 'modulation_53_amount', 'modulation_53_bipolar', 'modulation_53_bypass', 'modulation_53_power', 'modulation_53_stereo', 'modulation_54_amount', 'modulation_54_bipolar', 'modulation_54_bypass', 'modulation_54_power', 'modulation_54_stereo', 'modulation_55_amount', 'modulation_55_bipolar', 'modulation_55_bypass', 'modulation_55_power', 'modulation_55_stereo', 'modulation_56_amount', 'modulation_56_bipolar', 'modulation_56_bypass', 'modulation_56_power', 'modulation_56_stereo', 'modulation_57_amount', 'modulation_57_bipolar', 'modulation_57_bypass', 'modulation_57_power', 'modulation_57_stereo', 'modulation_58_amount', 'modulation_58_bipolar', 'modulation_58_bypass', 'modulation_58_power', 'modulation_58_stereo', 'modulation_59_amount', 'modulation_59_bipolar', 'modulation_59_bypass', 'modulation_59_power', 'modulation_59_stereo', 'modulation_60_amount', 'modulation_60_bipolar', 'modulation_60_bypass', 'modulation_60_power', 'modulation_60_stereo', 'modulation_61_amount', 'modulation_61_bipolar', 'modulation_61_bypass', 'modulation_61_power', 'modulation_61_stereo', 'modulation_62_amount', 'modulation_62_bipolar', 'modulation_62_bypass', 'modulation_62_power', 'modulation_62_stereo', 'modulation_63_amount', 'modulation_63_bipolar', 'modulation_63_bypass', 'modulation_63_power', 'modulation_63_stereo', 'modulation_64_amount', 'modulation_64_bipolar', 'modulation_64_bypass', 'modulation_64_power', 'modulation_64_stereo', 'compressor_mix', 'sample_bounce', 'voice_transpose', 'stereo_mode', 'chorus_filter_spread', 'reverb_delay', 'voice_override', 'bypass', 'lfo_1_transpose', 'lfo_1_tune', 'lfo_2_transpose', 'lfo_2_tune', 'lfo_3_transpose', 'lfo_3_tune', 'lfo_4_transpose', 'lfo_4_tune', 'lfo_5_transpose', 'lfo_5_tune', 'lfo_6_transpose', 'lfo_6_tune', 'lfo_7_transpose', 'lfo_7_tune', 'lfo_8_transpose', 'lfo_8_tune', 'random_lfo_1_transpose', 'random_lfo_1_tune', 'random_lfo_2_transpose', 'random_lfo_2_tune', 'random_lfo_3_transpose', 'random_lfo_3_tune', 'random_lfo_4_transpose', 'random_lfo_4_tune', 'filter_1_formant_spread', 'filter_2_formant_spread', 'filter_fx_formant_spread', 'lfo_1_smooth_mode', 'lfo_1_smooth_time', 'lfo_2_smooth_mode', 'lfo_2_smooth_time', 'lfo_3_smooth_mode', 'lfo_3_smooth_time', 'lfo_4_smooth_mode', 'lfo_4_smooth_time', 'lfo_5_smooth_mode', 'lfo_5_smooth_time', 'lfo_6_smooth_mode', 'lfo_6_smooth_time', 'lfo_7_smooth_mode', 'lfo_7_smooth_time', 'lfo_8_smooth_mode', 'lfo_8_smooth_time', 'view_spectrogram', 'oscillator_1_frequency_morph_phase', 'oscillator_2_frequency_morph_phase', 'oscillator_3_frequency_morph_phase'])

# Vital preset files are just .json files with a different suffix.
#   eg. /Users/devalias/Music/Vital/Factory/Presets/Plucked String.vital
#
#  ⇒ file "/Users/devalias/Music/Vital/Factory/Presets/Plucked String.vital"
# /Users/devalias/Music/Vital/Factory/Presets/Plucked String.vital: ASCII text, with very long lines (65536), with no line terminators
#
# They seem to hold the actual synth params within the 'settings' key', and there seem to be 775 parameters shown,
# which is the same as the number of parameters that we see in len(synth_plugin.parameters.keys())
#
# ⇒ jq '.settings | keys | length' "/Users/devalias/Music/Vital/Factory/Presets/Plucked String.vital"
# 775
