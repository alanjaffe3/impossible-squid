import numpy as np
from datetime import datetime
from trelli_text_gen import data_file
import os
import re
import pandas as pd

def test_text_file_check(tmp_path):

    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path, spectrum_length = data_file(
        tmp_path,
        date,
        "01",
        "LP5000.lan",
        "192.472.1.23",
        "TDLAS",
        [125000, 100, 1250, 300, 212, 115],
        -0.129348,
        0.0388757,
        [0, 0.548679, 0.92, 0.29283, 4.0],
        np.random.rand(10, 2),
        np.random.rand(10, 2),
    )

    # checks if the file exists
    assert os.path.exists(file_path)

    with open(file_path, "r") as f:
        contents = f.read()
        f.seek(0)
        lines = f.readlines()
        file_length = len(lines)
        date_line_new = lines[0].replace("\n", "")

        # checks if date is in correct format
        assert datetime.strptime(date_line_new, "%m/%d/%Y %H:%M:%S")

        # checks that the keyword for spectral analysis is in a recognized format
        spectraltechopt = lines[5].replace("\n", "")

        if spectraltechopt in ("TDLAS", "GBS", "LHR"):
            pass
        else:
            raise AssertionError("Invalid spectraltechopt value")

        # checks that keys exist
        assert "Sampling Rate (Hz)" in contents
        assert "Points for Column Avg" in contents
        assert "Laser Wave Freq (Hz)" in contents
        assert "Laser Current (uA)" in contents
        assert "Laser Temperature (C)" in contents
        assert "Laser Amplitude Scaling" in contents

        # checks if the dict values are in the correct format
        line_index = 7
        while line_index < 13:
            line = lines[line_index].strip()
            if not line:
                break
            if "\t" in line:
                key, value = line.split("\t")
            else:
                key, value = re.split(r"\s{2,}", line)
            # checks that values are float
            assert float(value)
            line_index += 1

    # assures the spectral data is in the correct format
    data = pd.read_csv(
        file_path, header=None, skiprows=file_length - spectrum_length, sep=r"\s+"
    )
    signal = data.iloc[:, 0]
    reference = data.iloc[:, 1]
