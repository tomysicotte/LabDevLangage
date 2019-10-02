"""
Author Tomy
"""

import os
from ParticipantClasses import ParticipantSmi, ParticipantObserver
from ProjectFct import *


def create_all_participant_smi(params):
    all_p = os.listdir(params["ParticipantFolder"])
    participant_list = []
    for p in all_p:
        p = ParticipantSmi(params, p)
        participant_list.append(p)
    return participant_list

def create_all_participant_observer(params):
    all_p = os.listdir(params["ParticipantFolder"])
    participant_list = []
    all_condition = csv_to_list(params['ConditionParticipantFile'], ';')
    for p in all_p:
        for participant in all_condition:
            if (" " + participant[0] + " " in p):
                p_condition = int(participant[1])
                p_real_name = participant[0]
        p_trials_info = get_trial_info(p_condition,params['ConditionTargetFile'])
        this_p = ParticipantObserver(params, p, p_condition, p_trials_info,p_real_name)
        participant_list.append(this_p)
    return participant_list


def get_trial_number(trial_name):
    trial_number = 0
    for i, letter in enumerate(trial_name):
        if trial_name[i:i + 5] == "Trial":
            trial_number = int(trial_name[i + 5:i + 8])
    return trial_number


def get_output(participant, p_col):
    p_output = [p_col]
    trials = participant.data_trial  # Dict
    p_before_col = p_col.index("Proportion before")
    p_after_col = p_col.index("Proportion after")
    for trial_name in sorted(trials):
        trial_output = [trial_name, get_trial_number(trial_name)]
        trial = trials[trial_name]

        trial_output = trial_output + n_duration_proportion_twindow(trial["All_Look"],
                                                                    participant.params["pre_twindow_beg"],
                                                                    participant.params["pre_twindow_end"])

        trial_output = trial_output + n_duration_proportion_twindow(trial["All_Look"],
                                                                    participant.params["post_twindow_beg"],
                                                                    participant.params["post_twindow_end"])

        trial_output = trial_output + first_look_info(trial["All_Look"], participant.params["post_twindow_beg"],
                                                      participant.params["post_twindow_end"],participant.name,trial_name)

        if (type(trial_output[p_after_col]) is not str) and (type(trial_output[p_before_col]) is not str) :
            trial_output.append(trial_output[p_after_col] - trial_output[p_before_col])
        else:
            trial_output.append("N/A")
        trial_output.append(trial["Type"])

        p_output.append(trial_output)

    return p_output
