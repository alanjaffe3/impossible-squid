# sensor_ui_new.py
# A DearPyGui-based UI to monitor Trellisense sensors from S3 bucket
# Displays sensor status, signal strength, position, and allows RealVNC connections

import dearpygui.dearpygui as dpg
import webbrowser
#import math
import re
#import time
#import threading
#from PIL import Image
import subprocess
import json
from datetime import datetime, timezone

global latest_files, tracker, date_st, time_st, signal, x_positions, y_positions, time_differential, temp_file_path, all_trackers

s = [
    "tracker1_20251009_222455_0.600_345_234",
    "tracker2_20250927_132455_0.500_645_178",
    "tracker3_20250721_092444_0.300_125_308",
    "tracker4_20251021_120055_0.060_785_978",
]

# with open('tracker_data.json', 'r') as file:
#   data = json.load(file)

# populate y with the names of the trackers and the id's for each of them
y = """[
    {"tracker": "tracker1", "id": "[tSdoL6-8h94s-AaskfY]"},
    {"tracker": "tracker4", "id": "[xAh7rh-7zcmZ-L3Ttc6]"},
    {"tracker": "tracker3", "id": "[ZDLxmg-bAH8L-xrz6tw]"},
    {"tracker": "tracker2", "id": "[4BVSkN-T2skU-VZQ8GV]"}
]"""

all_trackers = json.loads(y)

#'s' is a placeholder for 'bucket_name' amd 'prefix' in the bucket filter function


def _hyperlink(text, address):
    b = dpg.add_button(label=text, callback=lambda: webbrowser.open(address))
    dpg.bind_item_theme(b, "__demo_hyperlinkTheme")


def bucket_filter(filenames):
    global latest_files, tracker, date_st, time_st, signal, x_positions, y_positions, time_differential
    pattern = re.compile(r"(tracker\d+)_(\d{8})_(\d{6})_(\d+\.\d+)_(\d{3})_(\d{3})")

    latest_files = {}
    tracker = []
    date_st = []
    time_st = []
    signal = []
    x_positions = []
    y_positions = []
    time_differential = []

    for filename in filenames:
        match = pattern.search(filename)
        if not match:
            continue  # Skip files without date/time info

        # Extract date and time parts
        sensor, date_str, time_str, sig_level, x_pos, y_pos = match.groups()

        dt_obj = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")

        dt = dt_obj.replace(tzinfo=timezone.utc)
        timestamp_a = int(dt.timestamp())

        time_now = datetime.utcnow()
        time_now = time_now.replace(tzinfo=timezone.utc)
        timestamp = int(time_now.timestamp())

        time_diff = timestamp - timestamp_a

        time_differential.append((time_diff))

        path_match = re.search(r"tracker\d+", filename)
        # actual path names: s#(hiac,sudoe,etc etc)_.....
        if not path_match:
            continue
        path_id = path_match.group()

        # If this is the latest file for that path, store it
        if path_id not in latest_files or dt_obj > latest_files[path_id][0]:
            latest_files[path_id] = (dt_obj, filename)

            tracker.append((sensor))
            date_st.append((date_str))
            time_st.append((time_str))
            signal.append((sig_level))
            x_positions.append((x_pos))
            y_positions.append((y_pos))

    return (
        latest_files,
        tracker,
        date_st,
        time_st,
        signal,
        x_positions,
        y_positions,
        time_differential,
    )


def realvncsession(id):
    # the way to connect to each individual rpi will be different.
    # the obvious prerequisite is that you have realvnc downloaded.
    # 1. check the file path to get to "realvncviewer.exe" and paste it into the first set of quotations below
    # 2. open realvnc and open the rpi session you wish to connect to
    # 3. open the realvnc app
    # 4. in the menu, click "more ways to connect"
    # 5. copy paste the first line into the second set of quotations, should look something like "[tSdoL6-8h94s-AaskfY]"
    # 6. done!
    print(id)
    subprocess.Popen([r"C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe", str(id)])


# def image_viewer(sender, app_data, user_data):
#     file_path = user_data
#     image = Image.open(file_path)
#     width, height = image.size
#     with dpg.texture_registry(show=False):
#         dpg_image = dpg.load_image(file_path)
#         tex_id = dpg.add_static_texture(width, height, dpg_image)
#     with dpg.window(label=f"Image: {file_path}", width=width+50, height=height+80):
#         dpg.add_image(tex_id)


def make_realvncsession_callback(session_id):
    def callback(sender, app_data, user_data):
        realvncsession(session_id)

    return callback


def update_table():
    if not dpg.does_item_exist("table_body"):
        return

    rows = dpg.get_item_children("table_body", slot=1)
    for row in rows:
        dpg.delete_item(row)

    for i in range(len(s)):
        #'range(len(s))' will be replaced by 'sum(1 for _ in bucket.objects.all())' where bucket is just the bucket name
        with dpg.table_row(parent="table_body"):
            dpg.add_text(tracker[i])
            if int(time_differential[i]) > 10800:
                dpg.add_text("Offline", color=[255, 0, 0])
            else:
                dpg.add_text("Online", color=[0, 255, 0])
            dpg.add_text(date_st[i] + " " + time_st[i])
            if float(signal[i]) < 0.1:
                dpg.add_text("Weak Signal:" + signal[i] + "V", color=[251, 127, 43])
            else:
                dpg.add_text("Strong Signal:" + signal[i] + "V", color=[99, 187, 61])
            dpg.add_text(x_positions[i])
            dpg.add_text(y_positions[i])

            # creating buttons for vnc session
            match = next((t for t in all_trackers if t["tracker"] == tracker[i]), None)

            if match:
                dpg.add_button(
                    label=match["tracker"],
                    callback=make_realvncsession_callback(match["id"]),
                )
            else:
                print(f"No matching tracker found for '{tracker[i]}'")

        # code that has not been tested for image viewing

    # with dpg.window(label="S3 Images"):
    #     for i, file_path in enumerate(temp_file_path):
    #         dpg.add_button(label=f"View Image {i+1}", callback=view_image, user_data=file_path)


### if you would rather have a refresh button instead of continuous updates, keep the below function


def background_updater():
    bucket_filter(s)
    update_table()


### if you would rather have continuous updates rather than a refresh button, keep the below function

# def background_updater():
#     while dpg.is_dearpygui_running():
#         bucket_filter(s)     # refresh data
#         #same thing, 's' will be replaced by 'bucket_name, prefix'
#         # schedule table refresh safely on main thread
#         update_table()
#         time.sleep(3)  # refresh interval (in seconds)


def _sort_callback(sender, sort_specs):
    global latest_files, tracker, date, time, signal, x_positions, y_positions, time_differential

    # sort_specs scenarios:
    #   1. no sorting -> sort_specs == None
    #   2. single sorting -> sort_specs == [[column_id, direction]]
    #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
    #
    # notes:
    #   1. direction is ascending if == 1
    #   2. direction is ascending if == -1

    # no sorting case
    if sort_specs is None:
        return

    rows = dpg.get_item_children(sender, 1)

    # create a list that can be sorted based on first cell
    # value, keeping track of row and value used to sort
    sortable_list = []
    for row in rows:
        first_cell = dpg.get_item_children(row, 1)[0]
        sortable_list.append([row, dpg.get_value(first_cell)])

    def _sorter(e):
        return e[1]

    sortable_list.sort(key=_sorter, reverse=sort_specs[0][1] < 0)

    # create list of just sorted row ids
    new_order = []
    for pair in sortable_list:
        new_order.append(pair[0])

    dpg.reorder_items(sender, 1, new_order)


dpg.create_context()
dpg.create_viewport(title="Trellisense Sensor Tracker", width=750, height=400)

with dpg.window(tag="Main"):
    with dpg.group(horizontal=True):
        dpg.add_loading_indicator(circle_count=3)
        with dpg.group():
            dpg.add_text("Trellisense Sensor Library")
            with dpg.group(horizontal=True):
                dpg.add_text("Click the link for UI library documentation")
                _hyperlink(
                    "Link", "https://dearpygui.readthedocs.io/en/latest/index.html"
                )

    # button for manual refresh of table
    dpg.add_button(label="Refresh Entries", callback=background_updater)

    # dpg.add_button(label = "Scrape AWS S3", callback = bucket_filter(s))
    with dpg.table(
        tag="table_body",
        header_row=True,
        policy=dpg.mvTable_SizingFixedFit,
        row_background=True,
        borders_innerH=True,
        borders_outerH=True,
        borders_innerV=True,
        borders_outerV=True,
        scrollY=True,
        sortable=True,
        callback=_sort_callback,
    ):

        # use add_table_column to add columns to the table,
        # table columns use child slot 0
        dpg.add_table_column(label="Tracker Name")
        dpg.add_table_column(label="Activity")
        dpg.add_table_column(label="UTC Time Stamp")
        dpg.add_table_column(label="Signal Level")
        dpg.add_table_column(label="X-Position")
        dpg.add_table_column(label="Y-Position")
        dpg.add_table_column(label="RealVNC Session")

# Initial populate before thread starts
bucket_filter(s)
# replace 's' with 'bucket_name, prefix'
update_table()

### uncomment the below code if you plan on using cotinuous table refresh rather than button
# start background updater in its own thread
# dpg.set_frame_callback(1, lambda: threading.Thread(target=background_updater, daemon=True).start())

# launch GUI
dpg.set_primary_window("Main", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
