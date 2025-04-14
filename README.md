# Enhancing lateral overtaking distance for cyclist safety in the EU
This project defines a framework for evaluating different technologies in a traffic environment involving a cyclist and a vehicle. The jsPsych framework is used for the frontend. In the description below, it is assumed that the repository is stored in the folder cyclist-distance-crowdsourced. Terminal commands assume macOS.

## Setup
Tested with Python 3.9.12. To setup the environment run these two commands in a parent folder of the downloaded repository (replace `/` with `\` and possibly add `--user` if on Windows):
- `pip install -e cyclist-distance-crowdsourced` will setup the project as a package accessible in the environment.
- `pip install -r cyclist-distance-crowdsourced/requirements.txt` will install required packages.

### Configuration of project
Configuration of the project needs to be defined in `cyclist-distance-crowdsourced/config`. Please use the `default.config` file for the required structure of the file. If no custom config file is provided, `default.config` is used. The config file has the following parameters:
* `appen_job`: ID of the appen job.
* `num_stimuli`: number of stimuli in the study.
* `num_stimuli_participant`: subset of stimuli in the study shown to each participant.
* `allowed_min_time`: the cut-off for minimal time of participation for filtering.
* `num_repeat`: number of times each stimulus is repeated.
* `kp_resolution`: bin size in ms in which data is stored.
* `mask_id`: number for masking worker IDs in appen data.
* `allowed_stimulus_wrong_duration`: if the percentage of videos with abnormal length is above this value, exclude participant from analysis.
* `files_heroku`: files with data from heroku.
* `files_appen`: files with data from appen.
* `files_simulator`: files with data from the simulator experiment.
* `file_cheaters`: CSV file with cheaters for flagging.
* `path_source`: path with source files for the stimuli from the Unity3D project.
* `path_stimuli`: path consisting of all videos included in the survey.
* `mapping_stimuli`: CSV file that contains all data found in the videos.
* `plotly_template`: template used to make graphs in the analysis.
* `stimulus_width`: width of stimuli.
* `stimulus_height`: height of stimuli.
* `aoi`: csv file with AOI data.
* `smoothen_signal`: toggle to apply filter to smoothen data.,
* `freq`: frequency used by One Euro Filter.
* `mincutoff`: minimal cutoff used by One Euro Filter.
* `beta`: beta value used by One Euro Filter.
* `font_family`: font family to be used on the figures.
* `font_size`: font size to be used on the figures.
* `p_value`: p value used for ttest.
* `save_figures`: save "final" figures to the /figures folder.

## Preparation of stimuli
The source files of the video stimuli are outputted from Unity to `config.path_source`. To prepare them for the crowdsourced setup `python cyclist-distance-crowdsourced/preparation/process_videos.py`. Videos will be outputted to `config.path_stimuli`.

## Analysis
Analysis can be started by running python `cyclist-distance-crowdsourced/dcycl/run.py`. A number of CSV files used for data processing are saved in `cyclist-distance-crowdsourced/_output`. Visualisations of all data are saved in `cyclist-distance-crowdsourced/_output/figures/`.

## Keypress data
### All participants
[![kp_videos](figures/kp_videos.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos.html)
Percentage of participants pressing the response key as a function of elapsed video time for all stimuli for all participants.

[![kp_distance](figures/kp_distance-0.8-1.6-2.4.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_distance-0.8-1.6-2.4)
Percentage of participants pressing the response key as a function of elapsed video time for all stimuli grouped by distance.

[![kp_interaction](figures/kp_interaction-bike_laser_projection-vertical_sign-road_markings-car_laser_projection-control-unprotected_cycling_path-no_road_mark.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_interaction-bike_laser_projection-vertical_sign-road_markings-car_laser_projection-control-unprotected_cycling_path-no_road_mark.html)
Percentage of participants pressing the response key as a function of elapsed video time for grouped scenarios.

### Keypress Percentage by Scenario
[![plot_keypress_by_scenario 1](figures/kp_videos_sliders_0,1,2.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos_sliders_0%2C1%2C2.html)
 Percentage of participants pressing the response key as a function of elapsed video time and responses to post-stimulus questions for scenario 1.

[![plot_keypress_by_scenario 2](figures/kp_videos_sliders_3,4,5.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos_sliders_3%2C4%2C5.html)
Percentage of participants pressing the response key as a function of elapsed video time and responses to post-stimulus questions for scenario 2.

[![plot_keypress_by_scenario 3](figures/kp_videos_sliders_6,7,8.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos_sliders_6%2C7%2C8.html)
Percentage of participants pressing the response key as a function of elapsed video time and responses to post-stimulus questions for scenario 3.

[![plot_keypress_by_scenario 4](figures/kp_videos_sliders_9,10,11.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos_sliders_9%2C10%2C11.html)
Percentage of participants pressing the response key as a function of elapsed video time and responses to post-stimulus questions for scenario 4.

[![plot_keypress_by_scenario 5](figures/kp_videos_sliders_12,13,14.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos_sliders_12%2C13%2C14.htmll)
Percentage of participants pressing the response key as a function of elapsed video time and responses to post-stimulus questions for scenario 5.

[![plot_keypress_by_scenario 6](figures/kp_videos_sliders_15,16,17.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos_sliders_15%2C16%2C17.html)
Percentage of participants pressing the response key as a function of elapsed video time and responses to post-stimulus questions for scenario 6.

[![plot_keypress_by_scenario 7](figures/kp_videos_sliders_18,19,20.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/kp_videos_sliders_18%2C19%2C20.html)
Percentage of participants pressing the response key as a function of elapsed video time and responses to post-stimulus questions for scenario 7.

### Simulator experiment
[![min_distance](figures/min_distance.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/min_distance.html)
Mean distance of overtaking in the simulator experiment.

[![mean_speed](figures/mean_speed.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/mean_speed.html)
Mean speed of overtaking in the simulator experiment.

[![preferences](figures/preferences.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/preferences.html)
Preferences of concepts in simulator experiment.

[![overtaking distance](figures/overtaking_distance.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/overtaking_distance.html)
Average overtaking distance over time for different scenario.

#### Correlation and scatter matrices
![correlation matrix](https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/corr_matrix.jpg)
Correlation matrix.

[![scatter matrix](figures/scatter_matrix.png)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/scatter_matrix.html)  
Scatter matrix.

<!-- ## Area of Interest (AOI)
### For all participants
[![end-slider](figures/hist_end2-scenario_number-0.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/hist_end2-scenario_number-0.html)
Participants end slider responses to which scenario was most helpful.

[![end-slider 2](figures/hist_end2-slider-0-0.png?raw=true)](https://htmlpreview.github.io/?https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/hist_end2-slider-0-0.html)
Participants end slider responses experienced to stress. -->

#### Information on participants
[![end-slider 3](figures/hist_driving_freq.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/hist_driving_freq.html)
Participants driving experiences.

[![year of license](figures/map_year_license.png)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/map_year_license.html)  
Year of obtaining driver's license.

[![map of counts of participants](figures/map_counts.png)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/map_counts.html)  
Map of counts of participants.

[![map of age](figures/map_age.png)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/map_age.html)  
Map of age of participants.

[![map of gender](figures/map_gender.png)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/map_gender.html)  
Map of distribution of gender.

[![end-slider 4](figures/hist_cycling_freq.png?raw=true)](https://htmlpreview.github.io/?https://github.com/gip58/cyclist-distance-crowdsourced/blob/main/figures/hist_cycling_freq.html)
Participants cycling experiences.

## Troubleshooting
### Troubleshooting setup
#### ERROR: cyclist-distance-crowdsourced is not a valid editable requirement
Check that you are indeed in the parent folder for running command `pip install -e cyclist-distance-crowdsourced`. This command will not work from inside of the folder containing the repo.

