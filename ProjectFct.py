import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import statistics
import csv
import xlsxwriter

def csv_to_list(file_emplacement, delimiter):
    # Retourne une liste à partir d'un fichier CSV
    with open(file_emplacement, 'r') as f:
        my_reader = csv.reader((x.replace('\0', '') for x in f),delimiter=delimiter)
        my_info = list(my_reader)
    return my_info

def get_trial_info(condition,condition_trial_file) :
    condition_info = csv_to_list(condition_trial_file, ';')
    trials = []
    for info in condition_info[1:]:
        if int(info[0]) == condition :
            trial_index = int(info[1])
            trial_target = info[2]
            trial_type = int(info[3])-1
            trials.append([trial_index,trial_target,trial_type])
    return trials

def adjust_time(trial):
    """
    :param trial: liste des frames
    :return: liste ou le temps est le nombre de ms écouler depuis le temps 0
    """
    time_0 = float(trial[1][0])
    for i in range(1, len(trial)):
        trial[i][0] = (float(trial[i][0]) - time_0) / 1000.0
    return trial


def vf_time_window(look, t0, tend):
    t1 = 0.0
    t2 = 0.0
    if t0 < look["T_end"] and look["T0"] < tend:
        if look["T0"] < t0:
            t1 = t0
        else:
            t1 = look["T0"]
        if look["T_end"] > tend:
            t2 = tend
        else:
            t2 = look["T_end"]
    return [t1, t2, t2 - t1, look["Hit"]]


def vf_latency_window(look, t0, tend):
    t1 = 0.0
    t2 = 0.0
    if t0 < look[1] and look[0] < tend:
        if look[0] < t0:
            t1 = t0
        else:
            t1 = look[0]
        t2 = look[1]
    return [t1, t2, t2 - t1, look[3]]


def n_duration_proportion_twindow(trial, t0, tend):
    duration_target = 0.0
    duration_distractor = 0.0
    n_target = 0
    n_distractor = 0
    longest_target = 0
    longest_distractor = 0
    for look in trial:
        corrected_look = vf_time_window(look, t0, tend)
        if corrected_look[3] == 1:
            duration_target += corrected_look[2]
            if corrected_look[2] > 0:
                n_target += 1
                if corrected_look[2] > longest_target:
                    longest_target = corrected_look[2]
        elif corrected_look[3] == 2:
            duration_distractor += corrected_look[2]
            if corrected_look[2] > 0:
                n_distractor += 1
                if corrected_look[2] > longest_distractor:
                    longest_distractor = corrected_look[2]

    if duration_target + duration_distractor > 0:
        l_return = [n_target, n_distractor, duration_target, duration_distractor,
                    (duration_target / (duration_target + duration_distractor)),
                    longest_target, longest_distractor]
    else:
        l_return = [n_target, n_distractor, duration_target, duration_distractor,
                    "N/A",
                    longest_target, longest_distractor]

    return l_return


def first_look_info(trial, t0, tend,name,trial_name):
    output = []
    first_look_location = 0
    i = -1
    while first_look_location == 0:
        i += 1
        if trial[i]["T_end"] > t0:
            if trial[i]["T0"] < t0:
                first_look_location = trial[i]["Hit"]
            else:
                first_look_location = 3
    if first_look_location == 1:
        output.append("Target")
        cor_look = vf_latency_window([trial[i]["T0"], trial[i]["T_end"], trial[i]["Duration"], trial[i]["Hit"]], t0, tend)
        output.append(cor_look[2])
        output.append("")
    else:
        rt = 0
        for look in trial:
            if look["T_end"] > t0 and look["Hit"] == 1:
                if rt == 0:
                    rt = look["T0"] - t0

        if first_look_location == 2:
            output.append("Distractor")
        else:
            output.append('Outside')
        output.append("")
        output.append(rt)
    return output


def plot_graphs(params, type_dict):
    for k in type_dict:
        line_chance = [0.5] * len(type_dict[k][0])
    y_all = []
    y_all_average = []
    y_all_total_look = []
    my_file = xlsxwriter.Workbook(params["Exp name"] + " Graph_info" + '.xlsx')
    patches = []
    for k, keys in enumerate(type_dict):
        my_page = my_file.add_worksheet(name=keys)
        plt.figure(k + 1)
        y = []
        x = []
        for i in range(len(type_dict[keys][0]) - 1):
            target = float(type_dict[keys][0][i])
            dist = float(type_dict[keys][1][i])
            if len(y_all) - 1 < i:
                y_all.append([])
            if len(y_all_total_look) - 1 < i:
                y_all_total_look.append(target + dist)
            else:
                y_all_total_look[i] = y_all_total_look[i] + dist + target
            if dist+target == 0 :
                y.append(0.001)
                y_all[i].append(0.001)
            else :
                y.append(target / (dist + target))
                y_all[i].append(target / (dist + target))
            x.append(float(i))
            if k == len(type_dict) - 1:
                y_all_average.append(statistics.mean(y_all[i]))
        type_dict[keys] = y
        plt.plot(x, y)
        plt.plot(x, line_chance[0:len(x)], color='gray', linewidth=0.5)
        plt.ylabel("Ratio Look Target")
        plt.ylim((0, 1))
        plt.xlim((0, len(x)))
        plt.xlabel("Time (MS)")
        plt.title("Ratio pour " + keys)

        plt.figure(len(type_dict) + 1)
        plt.plot(x, y, color=params["Graph Colors"][k])
        patches.append(mpatches.Patch(color=params["Graph Colors"][k], label=keys))
        plt.legend(handles=patches)
        plt.plot(x, line_chance[0:len(x)], color='gray', linewidth=0.5)
        plt.ylabel("Ratio Look Target")
        plt.ylim((0, 1))
        plt.xlim((0, len(x)))
        plt.xlabel("Time (MS)")
        plt.title("Tous Overlap")
        my_page.write(0, 0, "Index")
        my_page.write(0, 1, "Temps")
        my_page.write(0, 2, "Proportion")
        for t, time in enumerate(x):
            my_page.write(t + 1, 0, t)
            my_page.write(t + 1, 1, time)
            my_page.write(t + 1, 2, y[t])

    plt.figure(len(type_dict) + 2)
    plt.plot(x, y_all_average)
    plt.plot(x, line_chance[0:len(x)], color='gray', linewidth=0.5)
    plt.ylabel("Ratio Look Target")
    plt.ylim((0, 1))
    plt.xlim((0, len(x)))
    plt.xlabel("Time (MS)")
    plt.title("Tous Average")
    my_page = my_file.add_worksheet(name="Average")
    my_page.write(0, 0, "Index")
    my_page.write(0, 1, "Temps")
    my_page.write(0, 2, "Proportion")
    for t, time in enumerate(x):
        my_page.write(t + 1, 0, t)
        my_page.write(t + 1, 1, time)
        my_page.write(t + 1, 2, y_all_average[t])

    plt.figure(len(type_dict) + 3)
    plt.plot(x, y_all_total_look[0:len(x)])
    plt.xlim((0, len(x)))
    plt.ylabel("Nombre look total")
    plt.xlabel("Time (MS)")
    plt.title("Rapport nombre de look")
    plt.show()
