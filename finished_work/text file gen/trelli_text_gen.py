from datetime import datetime
import re
import os

def data_file(
    file_location,
    date,
    path,
    hostname,
    ip,
    spectral_tech_opt,
    setup_info,
    ch0_offset,
    ch1_offset,
    methane_result,
    spectral_result_data,
    triangle_shifted_data,
):

    spectrum_length = len(spectral_result_data)
    assert len(setup_info) == 6

    # assign the values of setup_info to dict
    setup_info_dict = {
        "Sampling Rate (Hz)": setup_info[0],
        "Points for Column Avg": setup_info[1],
        "Laser Wave Freq (Hz)": setup_info[2],
        "Laser Current (uA)": setup_info[3],
        "Laser Temperature (C)": setup_info[4],
        "Laser Amplitude Scaling": setup_info[5],
    }

    filename = os.path.join(file_location, f"AVG_Path-{path}_{date}.txt")

    # create and write to a new file
    with open(filename, "w") as f:
        # convert date to expected format
        f.writelines(
            (
                datetime.strptime(date, "%Y%m%d_%H%M%S").strftime("%m/%d/%Y %H:%M:%S")
                + "\n",
                "\n",
                hostname + "\n",
                ip + "\n",
                "\n",
                spectral_tech_opt + "\n" "\n",
            )
        )
        # print dict values
        for key, value in setup_info_dict.items():
            f.writelines(f"{key}\t{value}\n")

        f.writelines(
            (
                "\n",
                str(ch0_offset) + "\n",
                str(ch1_offset) + "\n",
                "\n",
                # undetermined if this is the intended format
                str(methane_result[0])
                + " "
                + str(methane_result[1])
                + " "
                + str(methane_result[2])
                + " "
                + str(methane_result[3])
                + " "
                + str(methane_result[4])
                + "\n",
                "\n",
                # filter out brackets from numpy array
                re.sub(" ?[\[\]]", "", str(spectral_result_data)) + "\n",
                "\n",
                re.sub(" ?[\[\]]", "", str(triangle_shifted_data)),
            )
        )

        return filename, spectrum_length
