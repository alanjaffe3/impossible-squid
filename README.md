This repo is just a test for me to get used to GitHub, but I might just save all of my (Trellisense) coding projects in here anyways.

Currently, here are all of the projects that reside on this repo:

1. sensor_ui_new.py: This is for the dashboard project. The progress of this code is ongoing, but as it stands, it aims to take in data, either through AWS S3 or locally on an RPi, from our deployed sensors and display important information, such as voltage, activity, location, and active RealVNC connection options.
2. mock_read.py: Expansion code for the websocket script that resides in trellitrack. This just expands the available websockets from 1 to 2! An open port resides on 6340 via LabVIEW, and this allows the data streaming from LabVIEW to be accessibly on port 6341 and 6342, depending on the path.
3. mock_labview.py: Test script for mock_read.py before I learned what formalized test scripts were and how to make virtual environments. Can be ignored but kinda cool code to look at.
