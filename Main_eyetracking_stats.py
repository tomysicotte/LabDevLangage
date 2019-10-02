"""
Created on 2017-09-28

@author: Tomy Sicotte
"""

import json
import xlsxwriter
import DataMngFunction
from ProjectFct import plot_graphs


if __name__ == '__main__':
    #Nom du fichier de parametres
    json_path = "SMI_data_analysis_param.json"

    #Nom des colonnes du fichiers Excel
    p_col = ["Trial Name", "Trial Index", "Number of look on target (Before)",
             "Number of look on distractor (Before)", "Time on target before",
             "Time on distractor before", "Proportion before",
             'Longest look on target before', "Longest look on distractor before",
             "Number of look on target (After)", "Number of look on distractor (After)",
             "Time on target after", "Time on distractor after", "Proportion after",
             "Longest look  on target after", "Longest look  on distractor after",
             "First look location after", "Latency", "Reaction time", "Differential looking", "Condition"]

    #Ouver le fichier de parametre en tant que params
    with open(json_path, "r") as params_file:
        params = json.load(params_file)

    #Creer les participants
    if params['Type'] == "Eye Tracker":
        all_p = DataMngFunction.create_all_participant_smi(params)
    elif params['Type'] == "Observer":
        all_p = DataMngFunction.create_all_participant_observer(params)
    else :
        print("Erreur dans Params Type")
        all_p = []

    #Genere une liste de liste qui seront la page de chaque participant
    all_output = []
    for participant in all_p:
        all_output.append(DataMngFunction.get_output(participant, p_col))
    my_file = xlsxwriter.Workbook(all_p[0].params["Exp name"] + '.xlsx')

    type_dict = {}
    for i, participant in enumerate(all_p):
        # Preparation du fichier type_dict pour pyplot
        for trial in participant.data_trial:
            type_dict[participant.data_trial[trial]["Type"]] = [[0], [0]]

        #Ajoute la page dans le fichier excel
        my_page = my_file.add_worksheet(name=participant.real_name)
        for t, trial in enumerate(all_output[i]):
            for info_i in range(len(trial)):
                my_page.write(t, info_i, all_output[i][t][info_i])

    #incremente dans le fichier type dict pour avoir les ratios
    for participant in all_p:
        for trial in participant.data_trial:
            for i, frame in enumerate(participant.data_trial[trial]["Frame_Hit"]):
                if len(type_dict[participant.data_trial[trial]["Type"]][0]) < i+1:
                    type_dict[participant.data_trial[trial]["Type"]][0].append(0)
                if len(type_dict[participant.data_trial[trial]["Type"]][1]) < i + 1:
                    type_dict[participant.data_trial[trial]["Type"]][1].append(0)
                if frame == 1:
                    type_dict[participant.data_trial[trial]["Type"]][0][i] += 1
                elif frame == 2:
                    type_dict[participant.data_trial[trial]["Type"]][1][i] += 1

    plot_graphs(params, type_dict)
    my_file.close()
