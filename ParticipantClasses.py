"""
Created on 2017-09-28

@author: tsico
"""
import os
from ProjectFct import *


class ParticipantSmi(object):
    def __init__(self, params, p_name):
        self.params = params
        self.name = p_name
        self.real_name = p_name

        self.path = self.params["ParticipantFolder"] + "\\" + self.name
        self.name_trials = os.listdir(self.path)
        self.raw_trial_info = {}
        self.data_trial = {}
        for trial in self.name_trials:
            self.raw_trial_info[trial] = csv_to_list(self.path + "\\" + trial, self.params["Delimiter"])
            trial_data = self.trial_info(self.raw_trial_info[trial])
            trial_data = adjust_time(trial_data) # Le temps devient en ms et commence a 0
            this_trial = self.eval_frame(trial_data)
            frame_time = []
            frame_hit = []
            for ms in range(self.params["TrialDuration"]):
                frame_time.append(ms)
                hit = 0
                for look in this_trial["All_Look"]:
                    if look["T0"] <= ms <= look["T_end"]:
                        hit = look["Hit"]
                frame_hit.append(hit)
            this_trial["Frame_Hit"] = frame_hit
            this_trial["Frame_Time"] = frame_time
            self.data_trial[trial] = this_trial

    def trial_info(self,trial):
        """
        :param trial: liste provenant d'un fichier csv pour un trial
        :return: Une liste contenant seulement les données des frames et les noms de chaque colone dans liste[0]
        """
        useful_frame = []
        for this_frame in trial:
            if this_frame[0] == self.params["TimeCol"]:
                useful_frame.append(this_frame)
            else:
                try:
                    this_frame[0] = int(this_frame[0])
                    useful_frame.append(this_frame)
                except ValueError:
                    continue
        return useful_frame

    def eval_frame(self, trial):
        time_col = trial[0].index(self.params["TimeCol"])
        aoi_hit_col = trial[0].index(self.params["AOI"])
        trial_data = {"Frame_Time": [],
                    "Frame_Hit": [],
                    "Type": ""}
        for frame in trial[1:]:
            trial_data["Frame_Time"].append(frame[time_col])
            if frame[aoi_hit_col].find(self.params["Condition1 Hit"]) >= 0 :
                trial_data["Frame_Hit"].append(1)
                for condition in self.params["Condition2"] :
                    if frame[aoi_hit_col].find(condition+" ") == 0 or frame[aoi_hit_col].find(" " +condition) > 0:
                        trial_data["Type"] = "Target = " + condition
                if trial_data["Type"] == "" :
                    trial_data["Type"] = "Erreur dans le input"
            elif frame[aoi_hit_col].find(self.params["Condition1 Miss"]) >= 0 :
                trial_data["Frame_Hit"].append(2)
            else :
                trial_data["Frame_Hit"].append(0)

        trial_data = self.get_good_look(trial_data)
        return trial_data

    def get_good_look(self, trial_data):
        """
        :return: ajoute au dictionnaire une cle 'All_Look' ayant pour valeur une liste un dictionnaire pour
         chaque fixation(liste(debut fixation, fin fixation, duree, 1 = target ou 2 = distracteur))
        """
        trial_data["All_Look"] = []
        last_event = 0
        bgn_event = 0.0
        for i, frame in enumerate(trial_data["Frame_Hit"]):
            if frame != last_event or i == len(trial_data["Frame_Hit"]) - 1:
                if last_event == 0 :
                    last_event = frame
                    bgn_event = trial_data["Frame_Time"][i]
                else:
                    fixation = {"T0" : bgn_event,
                                "T_end": trial_data["Frame_Time"][i-1],
                                "Duration": trial_data["Frame_Time"][i-1] - bgn_event,
                                "Hit" : last_event}
                    trial_data["All_Look"].append(fixation)
                    last_event = frame
                    bgn_event = trial_data["Frame_Time"][i]
        return trial_data


class ParticipantObserver(object):
    def __init__(self, params, p_name, condition, trials_info,real_name):
        self.params = params
        self.name = p_name
        self.condition = condition
        self.trials_info = trials_info
        self.path = self.params["ParticipantFolder"]
        self.raw_trials = self.seperate_trials()
        self.data_trial = {}
        self.real_name = real_name
        for t,trial in enumerate(self.raw_trials):
            if t < 9:
                trial_name = "Trial00" + str(int(t)+1)
            else:
                trial_name = "Trial0" + str(int(t)+1)
            self.data_trial[trial_name] = self.get_trial_info(t)

    def seperate_trials(self):
        all_trials_raw = csv_to_list(self.params["ParticipantFolder"]+self.name, self.params['Delimiter'])
        all_trials_raw = all_trials_raw[1:]
        trials = []
        i_beg = 0
        t0 = 0
        event_col = self.params["BehaviorColIndex"]-1
        event_state_col = self.params["StateColIndex"]-1
        time_col = self.params["TimeColIndex"]-1
        for i, line in enumerate(all_trials_raw):
            if len(line) > 1:
                if line[event_col] == self.params["BehavioralTrialIndicator"]:
                    if line[event_state_col] == "State start":
                        i_beg = i
                        t0 = int(float(line[time_col].replace(",", ".")) * 1000)
                    elif line[event_state_col] == "State stop":
                        this_trial = []
                        for trial_line in all_trials_raw[i_beg:i + 1]:
                            if len(trial_line) > 1:
                                time_info = int(float(trial_line[time_col].replace(",", ".")) * 1000) - t0
                                behav = trial_line[event_col]
                                state = trial_line[event_state_col]
                                this_trial.append([time_info, behav, state])
                        trials.append(this_trial)
        return trials

    def get_trial_info(self,t):
        trial_info = {}
        this_trial = self.raw_trials[t]
        target_side = self.trials_info[t][1]
        trial_info["Type"] = self.params["TrialType"][int(self.trials_info[t][2])-1]
        all_look = []
        frame_hit = []
        frame_time = []
        for i,line in enumerate(this_trial) :
            if (line[1] == self.params["BehavioralRightIndicator"] or line[1] == self.params["BehavioralLeftIndicator"]) and \
                            line[2] == "State start":
                if len(all_look) == 0 :
                    this_look = {}
                    this_look["T0"] = 0
                    this_look["T_end"] = line[0]
                    this_look["Duration"] = line[0]
                    this_look["Hit"] = 3
                    all_look.append(this_look)
                elif line[0] > all_look[len(all_look)-1]["T_end"] :
                    this_look = {}
                    this_look["T0"] = all_look[len(all_look)-1]["T_end"]
                    this_look["T_end"] = line[0]
                    this_look["Duration"] = this_look["T_end"] - this_look["T0"]
                    this_look["Hit"] = 3
                    all_look.append(this_look)
                this_look = {}
                this_look["T0"] = line[0]
                t_end = 0
                if (target_side == "Right" and line[1]==self.params["BehavioralRightIndicator"]) or \
                        (target_side == "Left" and line[1] == self.params["BehavioralLeftIndicator"]) :
                    this_look["Hit"] = 1
                else:
                    this_look["Hit"] = 2
                for other_lines in this_trial[i:] :
                    if other_lines[1] == line[1] and other_lines[2] == "State stop" and t_end == 0:
                        t_end = other_lines[0]
                if t_end == 0 :
                    t_end = this_trial[len(this_trial)-1][0]
                this_look["T_end"] = t_end
                this_look["Duration"] = t_end-this_look["T0"]
                all_look.append(this_look)
        if len(all_look) > 0:
            if all_look[(len(all_look)-1)]["T_end"] < self.params["TrialDuration"]:
                this_look = {}
                this_look["T0"] = all_look[(len(all_look)-1)]["T_end"]
                this_look["T_end"] = self.params["TrialDuration"]
                this_look["Duration"] = this_look["T_end"] - this_look["T0"]
                this_look["Hit"] = 3
                all_look.append(this_look)
        else :
            this_look = {}
            this_look["T0"] = 0
            this_look["T_end"] = self.params["TrialDuration"]
            this_look["Duration"] = self.params["TrialDuration"]
            this_look["Hit"] = 0
            all_look.append(this_look)

        for ms in range(self.params["TrialDuration"]) :
            frame_time.append(ms)
            hit = 0
            for look in all_look:
                if look["T0"] <= ms <= look["T_end"] :
                    hit = look["Hit"]
            frame_hit.append(hit)
        trial_info["All_Look"] = all_look
        trial_info["Frame_Hit"] = frame_hit
        trial_info["Frame_Time"] = frame_time
        return trial_info

