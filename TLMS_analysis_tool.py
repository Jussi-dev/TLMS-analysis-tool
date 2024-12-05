import tkinter as tk
import sys
import os
import json

mla_path = os.path.abspath(r'C:\Users\henttju\Python scripts\TLMS log analysis\TLMS MeasureResults')
if mla_path not in sys.path:
    sys.path.append(mla_path)
    print("Path added: " + mla_path)
import Measureresult_log_analysis as mla

fva_path = os.path.abspath(r'C:\Users\henttju\Python scripts\Search in FV logs')
if fva_path not in sys.path:
    sys.path.append(fva_path)
    print("Path added: " + fva_path)
import Search_FV_log as sfl

def launch_tlms_log_parse():
    print("TLMS log parse launched")
    file_path = mla.process_measurement_logs()
    print("File path: " + file_path)

    # Create a 'logs' folder if it doesn't exist
    copy_file_to_logs(file_path)

# ==================== Fleet View Alarm Search ====================
# Fleet View alarm search is initialized by editing the Config.json file
# Editing the Config.json file involves selecting the ASC and the alarm to search for
# with a GUI interface
def initialize_fv_alarm_search():
    # Import 'Config.json' file from Search_FV_log root
    config_path = os.path.join(fva_path, 'Config.json')
    # Read the 'Config.json' file as a json object
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # Get the logs folder and source from the 'Config.json' file
    logs_folder_name, source = sfl.get_logs_folder_and_source(config)

    # Find parsing-output folder
    logs_folder_path = os.path.join(fva_path, logs_folder_name) # Get the full path of the logs folder in the Search_FV_log root
    parsing_output_folder = sfl.find_parsing_output_folder(logs_folder_path) # Find the parsing-output folder in the logs folder
    if not parsing_output_folder:
        print("Parsing output folder not found.")
        return

    # ==================== Select ASC ====================
    asc_selection_window = tk.Toplevel()
    asc_selection_window.title("Select ASC")

    # Create a listbox to display ASC names
    asc_listbox = tk.Listbox(asc_selection_window, selectmode=tk.SINGLE)

    # List ASCs in the parsing-output folder
    source_asc_list = list_asc_names(parsing_output_folder)

    # Populate the listbox with ASC names
    for asc in source_asc_list:
        asc_listbox.insert(tk.END, asc)
    asc_listbox.pack(pady=10)
    
    # Create a button to confirm selection
    btn_select_asc = tk.Button(asc_selection_window, text="Select", command=lambda: on_asc_select(asc_listbox, asc_selection_window, config, config_path, parsing_output_folder))
    btn_select_asc.pack(pady=10)
    # ===================================================

def on_asc_select(asc_listbox, asc_selection_window, config, config_path, parsing_output_folder):
    selected_asc = asc_listbox.get(tk.ACTIVE)
    print("Selected ASC: " + selected_asc)
    asc_selection_window.destroy()
    # Write selected ASC as the source in the 'Config.json' file
    if 'program_setup' in config and 'settings' in config['program_setup']:
        config['program_setup']['settings']['source'] = selected_asc
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        # Create alarm selection window
        create_alarm_selection_window(config, config_path, parsing_output_folder)

def create_alarm_selection_window(config, config_path, parsing_output_folder):
    # ==================== Select Alarm ====================
    # Create a listbox to display alarm names
    alarm_selection_window = tk.Toplevel()
    alarm_selection_window.title("Select Alarm")

    # Create a listbox to display alarm names
    alarm_listbox = tk.Listbox(alarm_selection_window, selectmode=tk.SINGLE)

    # List alarms in the source alarm file
    source = config['program_setup']['settings']['source']
    source_alarm_file = os.path.join(parsing_output_folder, source + '_stats.txt')
    source_alarm_list = sfl.list_alarm_names(source_alarm_file)

    # Set the width of the listbox based on the longest alarm name
    max_alarm_length = max(len(alarm) for alarm in source_alarm_list)
    alarm_listbox.config(width=max_alarm_length + 5) # Add some padding
    
    # Populate the listbox with alarm names
    for alarm in source_alarm_list:
        alarm_listbox.insert(tk.END, alarm)

    # Create a button to confirm selection
    btn_select_alarm = tk.Button(alarm_selection_window, text="Select", command=lambda: on_alarm_select(alarm_listbox, alarm_selection_window, config, config_path))
    
    alarm_listbox.pack(pady=10)
    btn_select_alarm.pack(pady=10)


def on_alarm_select(alarm_listbox, alarm_selection_window, config, config_path):
    selected_alarm = alarm_listbox.get(tk.ACTIVE)
    print("Selected Alarm: " + selected_alarm)
    alarm_selection_window.destroy()
    # Write selected alarm to the 'Config.json' file
    if 'program_setup' in config and 'settings' in config['program_setup']:
        config['program_setup']['settings']['alarm_text'] = selected_alarm
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        # Create alarm search launch window
        create_alarm_search_launch_window()
        

def list_asc_names(parsing_output_folder):
    asc_names = []
    for file_name in os.listdir(parsing_output_folder): # List all files in the parsing-output folder
        if file_name.startswith('ASC'): # Check if the file name starts with 'ASC'
            asc = file_name.split('_')[0] # Get the ASC name
            asc_names.append(asc)
        else:
            print(f"File '{file_name}' is not an ASC alarm file")
    return asc_names

def create_alarm_search_launch_window():
    alarm_search_launch_window = tk.Toplevel()
    alarm_search_launch_window.title("Launch Alarm Search")

    # Create a button to launch alarm search
    btn_launch_alarm_search = tk.Button(alarm_search_launch_window, text="Launch Alarm Search", command=lambda: launch_alarm_search(alarm_search_launch_window))

    # Create buttom for MeasureResult copy over
    btn_copy_measure_result = tk.Button(alarm_search_launch_window, text="Copy MeasureResult", command=copy_measure_result)

    # Pack the widgets
    btn_launch_alarm_search.pack(pady=10)
    btn_copy_measure_result.pack(pady=10)


def launch_alarm_search(alarm_search_launch_window):
    print("Alarm search launched")
    alarm_search_launch_window.destroy()
    matched_results_path = sfl.process_fv_logs()

    #Copy the file to the 'logs' folder
    copy_file_to_logs(matched_results_path)

# Copy the file to the 'logs' folder
def copy_file_to_logs(file_path):
    logs_folder = os.path.join(os.getcwd(), 'logs') # Get the 'logs' folder in the current working directory
    if not os.path.exists(logs_folder): # Check if the 'logs' folder exists
        os.makedirs(logs_folder) # Create the 'logs' folder if it doesn't exist

    # Copy the file to the 'logs' folder
    file_name = os.path.basename(file_path) # Get the file name from the file path
    logs_file_path = os.path.join(logs_folder, file_name) # Get the full path of the file in the 'logs' folder
    os.replace(file_path, logs_file_path) # Copy the file to the 'logs' folder
    print(f"File {file_name} copied to: {logs_file_path}")
    
# Copy the MeasureResult.xlsx in local 'logs' folder to
# the Search_FV_log -> logs -> MeasureResult-parsed folder
def copy_measure_result():
    print("Copying Measureresult")
    # Get the source folder and file
    source_file = os.path.join(os.getcwd(), 'logs', 'Measureresult.xlsx')
    print("Source file: " + source_file)
    # Check if the source file exists
    if not os.path.exists(source_file):
        print("Source file not found.")
        return
    else:
        print("Source file found.")
        # Get the destination folder
        destination_folder = os.path.join(fva_path, 'logs', 'MeasureResult-parsed')
        # Check if the destination folder exists
        if not os.path.exists(destination_folder):
            print("Destination folder not found.")
            return
        else:
            print("Destination folder found.")
            # Copy the source file to the destination folder
            destination_file = os.path.join(destination_folder, 'Measureresult.xlsx')
            os.replace(source_file, destination_file)
            print("File copied to: " + destination_file)
    
def main():
    root = tk.Tk()
    root.title("TLMS Analysis Tool")

    # Create a buttons
    btn_tlms_result_parse = tk.Button(root, text="Launch TLMS log parse", command=launch_tlms_log_parse) # Launch TLMS log parse button
    btn_fleet_view_alarm_search = tk.Button(root, text="Launch Fleet View Alarm Search", command=initialize_fv_alarm_search) # Launch Fleet View alarm search button

    # Pack the buttons
    btn_fleet_view_alarm_search.pack(pady=10)
    btn_tlms_result_parse.pack(pady=10)

    # Run the application
    root.mainloop()

if __name__ == '__main__':
    main()