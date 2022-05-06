import tkinter as tk
import os
from tkinter import filedialog
import math
import pandas as pd
import csv
import scipy.stats as stats
from datetime import datetime



# pyinstaller.exe --onefile --icon=office_folder.ico language_processing_gui.py
# language algorithm

def printPowerSet(set, set_size, variable):
    # set_size of power set of a set
    # with set_size n is (2**n -1)
    pow_set_size = (int)(math.pow(2, set_size))
    counter = 0
    j = 0
    inner_list = []
    # Run from counter 000..0 to 111..1
    for counter in range(0, pow_set_size):
        for j in range(0, set_size):

            # Check if jth bit in the
            # counter is set If set then
            # print jth element from set
            if ((counter & (1 << j)) > 0):
                inner_list.append(set[j])
                # print(set[j], end="")

        variable.append(inner_list)
        inner_list = []
        # print("")

    return variable


def return_percentage_for_combo(individual_combo, sard_data, column_name_list):
    combo_string = str(individual_combo)
    combo_string = combo_string.strip("[]")
    combo_string = combo_string.replace(",", "/")

    output_list = [combo_string]
    # everything w lists seems to be happening fast, pandas seems slow!!!
    # could I make these two lines better w standard python?
    combo_df = sard_data.loc[sard_data.lang_id.isin(individual_combo)]
    outside_of_combo_df = sard_data.loc[~sard_data.lang_id.isin(individual_combo)]

    # print(column_name_list)

    for col in column_name_list:
        # print(col)
        yes_list = []
        no_list = []
        final_contingency_table = []

        if col != "lang_id":
            cumulative_list = list(combo_df[col])
            cumulative_list_outside = list(outside_of_combo_df[col])
            # print("inside if")
            # print(cumulative_list)
            try:
                # print("inside try")
                yes_in_total = sum(cumulative_list)
                yes_list.append(yes_in_total)
                no_in_total = len(cumulative_list) - sum(cumulative_list)
                no_list.append(no_in_total)
                yes_out_total = sum(cumulative_list_outside)
                yes_list.append(yes_out_total)
                no_out_total = len(cumulative_list_outside) - sum(cumulative_list_outside)
                no_list.append(no_out_total)
                final_contingency_table.append(yes_list)
                final_contingency_table.append(no_list)
                oddsratio, pvalue = stats.fisher_exact(final_contingency_table, alternative="greater")

                output_list.append(pvalue)
            except:
                pass
    '''
    final_value = output_list[1] * output_list[2] * output_list[3] * output_list[4] * output_list[5] * output_list[6] * \
                  output_list[7] * output_list[8] * output_list[9] * \
                  output_list[10] * output_list[11] * output_list[12] * output_list[13] * output_list[14] * output_list[
                      15] * output_list[16] * output_list[17]

    output_list.append(final_value)
    '''


    return output_list

def print_status_update_for_user(num_rows, total_rows, start_time):
    #print('Processed this many rows: ' + str(num_rows) + ' out of a total of: ' + str(total_rows))
    current_time = datetime.now()
    run_time = current_time - start_time
    return 'Processed this many rows: ' + str(num_rows) + ' out of a total of: ' + str(total_rows) + ' in ' + str(run_time)

def process_uniq_combos_and_make_csv(input_file_path, output_file_name):
    # r"C:\Users\rober\Desktop\sardinian_input_may_6_2021.csv"
    start_time = datetime.now()
    sard_data = pd.read_csv(input_file_path)
    column_name_list = sard_data.columns.values.tolist()
    lang_id_list = list(sard_data["lang_id"])
    variable = []
    uniq_combo_list = printPowerSet(lang_id_list, len(lang_id_list), variable)
    list_of_output_lists = []
    output_count = 0

    for uniq_combo in uniq_combo_list:
        if len(uniq_combo) > 1:
            percentage_list = return_percentage_for_combo(uniq_combo, sard_data, column_name_list)
            # print(percentage_list)
            list_of_output_lists.append(percentage_list)
            output_count += 1

            if output_count % 1000 == 0:
                print("done with this much output: " + str(output_count) + " rows")
                message_string = print_status_update_for_user(output_count, len(uniq_combo_list), start_time)
                message_to_user['text'] = message_string
                # allows message to be printed, otherwise app becomes non responsive
                root.update()

    #column_name_list.remove('lang_id')
    fishers_output_df = pd.DataFrame(list_of_output_lists, columns = column_name_list)
    fishers_output_df['final_value'] = fishers_output_df[list(fishers_output_df.columns[1:])].product(axis = 1)
    folder_name = os.path.dirname(input_file_path)
    output_file_path = folder_name + "/" + output_file_name + '.csv'
    with open(output_file_path, "w", newline='') as csv_output:
        wr = csv.writer(csv_output, column_name_list)
        column_name_list.append('final output')
        wr.writerow(column_name_list)
        wr.writerows(list_of_output_lists)

    message_to_user['text'] = 'Finished run of ' + str(len(uniq_combo_list)) + ' rows'


input_file_name = ''
def user_picks_file():

    global input_file_name
    root.filename = filedialog.askopenfilename(initialdir="/", title="choose input file")
    input_file_name = root.filename
    user_file_path_to_show['text'] = 'file path of input: \n' + input_file_name


# tkinter
root = tk.Tk()

HEIGHT = 500
WIDTH = 500
canvas = tk.Canvas(root, height = HEIGHT, width = WIDTH, bg = '#D0B49F')
canvas.pack()

frame = tk.Frame(root, bg = '#9EC2E7')
frame.place(relwidth = .8, relheight = .2, rely = 0, relx = .1)

file_picker_button = tk.Button(frame, text = "Choose File", command = lambda: user_picks_file(), \
                               bg = '#9F9EE7')
file_picker_button.pack()

output_label = tk.Label(frame, text = "Enter Name of Output file. \n \
(If the same filename exists in the folder, the file will be overwritten)", bg = '#C39EE7')
output_label.pack()

output_entry = tk.Entry(frame)
output_entry.pack()

button = tk.Button(frame, text = "Analyze", \
command = lambda: process_uniq_combos_and_make_csv(input_file_name, output_entry.get()), \
bg = '#9EE7CB')
button.pack()

lower_frame = tk.Frame(root, bg = '#BAE79E' )
lower_frame.place(relwidth = .8, relheight = .5, rely = .5, relx = .1)

user_file_path_to_show = tk.Label(lower_frame, bg = '#A79EE7')
user_file_path_to_show.pack()


message_to_user = tk.Label(lower_frame, bg = '#F1E473')
message_to_user.pack()

root.mainloop()
