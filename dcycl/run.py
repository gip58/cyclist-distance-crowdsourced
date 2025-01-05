# by Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>
import matplotlib.pyplot as plt
import matplotlib._pylab_helpers
from tqdm import tqdm
import os
from statistics import mean
import dcycl as dc
dc.logs(show_level='info', show_color=True)
logger = dc.CustomLogger(__name__)  # use custom logger

# const
# SAVE_P = True  # save pickle files with data
# LOAD_P = False  # load pickle files with data
# SAVE_CSV = True  # load csv files with data
# FILTER_DATA = True  # filter Appen and heroku data
# CLEAN_DATA = True  # clean Appen data
# REJECT_CHEATERS = False  # reject cheaters on Appen
# CALC_COORDS = False  # extract points from heroku data
# UPDATE_MAPPING = True  # update mapping with keypress data
# SHOW_OUTPUT = True  # should figures be plotted
# SHOW_OUTPUT_KP = True  # should figures with keypress data be plotted-
# SHOW_OUTPUT_ST = True  # should figures with stimulus data to be plotted
# SHOW_OUTPUT_PP = True  # should figures with info about participants
# SHOW_OUTPUT_ET = False  # should figures for eye tracking

# for debugging, skip processing
SAVE_P = True  # save pickle files with data
LOAD_P = False  # load pickle files with data
SAVE_CSV = True  # load csv files with data
FILTER_DATA = True  # filter Appen and heroku data
CLEAN_DATA = True  # clean Appen data
REJECT_CHEATERS = False  # reject cheaters on Appen
CALC_COORDS = False  # extract points from heroku data
UPDATE_MAPPING = False  # update mapping with keypress data
SHOW_OUTPUT = True  # should figures be plotted
SHOW_OUTPUT_KP = True  # should figures with keypress data be plotted
SHOW_OUTPUT_ST = False  # should figures with stimulus data be plotted
SHOW_OUTPUT_PP = False  # should figures with info about participants be plotted
SHOW_OUTPUT_ET = False  # should figures for eye tracking be plotted

file_mapping = 'mapping.p'  # file to save updated mapping
file_coords = 'coords.p'  # file to save lists with coordinates

if __name__ == '__main__':
    # create object for working with heroku data
    files_heroku = dc.common.get_configs('files_heroku')
    heroku = dc.analysis.Heroku(files_data=files_heroku, save_p=SAVE_P, load_p=LOAD_P, save_csv=SAVE_CSV)
    # read heroku data
    heroku_data = heroku.read_data(filter_data=FILTER_DATA)

    # create object for working with appen data
    file_appen = dc.common.get_configs('file_appen')
    appen = dc.analysis.Appen(file_data=file_appen, save_p=SAVE_P, load_p=LOAD_P, save_csv=SAVE_CSV)
    # read appen data
    appen_data = appen.read_data(filter_data=FILTER_DATA, clean_data=CLEAN_DATA)
    # read frames
    # get keys in data files
    heroku_data_keys = heroku_data.keys()
    appen_data_keys = appen_data.keys()
    # flag and reject cheaters
    if REJECT_CHEATERS:
        qa = dc.analysis.QA(file_cheaters=dc.common.get_configs('file_cheaters'),
                            job_id=dc.common.get_configs('appen_job'))
        qa.reject_users()
        qa.ban_users()
    # merge heroku and appen dataframes into one
    all_data = heroku_data.merge(appen_data, left_on='worker_code', right_on='worker_code')
    logger.info('Data from {} participants included in analysis.', all_data.shape[0])
    heroku_data = all_data[all_data.columns.intersection(heroku_data_keys)]
    appen_data = all_data[all_data.columns.intersection(appen_data_keys)]
    heroku_data = heroku_data.set_index('worker_code')
    heroku.set_data(heroku_data)  # update object with filtered data
    appen_data = appen_data.set_index('worker_code')
    appen.set_data(appen_data)  # update object with filtered data
    appen.show_info()  # show info for filtered data
    # generate country-specific data
    countries_data = appen.process_countries()
    # create arrays with coordinates for stimuli
    if CALC_COORDS:
        points, _, points_duration = heroku.points(heroku_data)
        dc.common.save_to_p(file_coords, [points, points_duration], 'points data')
    else:
        points, points_duration = dc.common.load_from_p(file_coords, 'points data')
    # update mapping with keypress data
    if UPDATE_MAPPING:
        # read in mapping of stimuli
        mapping = heroku.read_mapping()
        # process keypresses and update mapping
        mapping = heroku.process_kp(filter_length=False)
        # post-trial questions to process
        questions = [{'question': 'slider-0', 'type': 'num'},
                     {'question': 'slider-1', 'type': 'num'}]
        # process post-trial questions and update mapping
        mapping = heroku.process_stimulus_questions(questions)
        # rename columns with responses to post-stimulus questions to meaningful names
        mapping = mapping.rename(columns={'slider-0': 'space',
                                          'slider-1': 'estimate'})
        # export to pickle
        dc.common.save_to_p(file_mapping, mapping, 'mapping of stimuli')
    else:
        mapping = dc.common.load_from_p(file_mapping, 'mapping of stimuli')
    # Output
    if SHOW_OUTPUT:
        analysis = dc.analysis.Analysis()
        num_stimuli = dc.common.get_configs('num_stimuli')
        logger.info('Creating figures.')
        # Visualisation of keypress data
        if SHOW_OUTPUT_KP:
            # all keypresses with confidence interval
            analysis.plot_kp(mapping,
                             conf_interval=0.95,
                             save_file=True,
                             save_final=dc.common.get_configs('save_figures'))
            # keypresses of groups of stimuli
            logger.info('Creating bar plots of keypress data for groups of stimuli.')
            for stim in tqdm(range(int(num_stimuli/3))):  # tqdm adds progress bar
                # ids of stimuli that belong to the same group
                ids = [stim*3, stim*3 + 1, stim*3 + 2]
                df = mapping[mapping['id'].isin(ids)]
                # extract timestamps of events
                events = []
                # add info to dictionary of events to be passed for plotting
                events.append({'id': 1,
                               'start': df.loc['video_' + str(ids[0]), 'overtake'] / 1000,  # type: ignore
                               'end': df.loc['video_' + str(ids[0]), 'overtake'] / 1000,  # type: ignore
                               'annotation': None})
                # prepare pairs of signals to compare with ttest
                ttest_signals = [{'signal_1': df.loc['video_' + str(ids[0])]['kp_raw'][0],  # 0 and 1 = between
                                  'signal_2': df.loc['video_' + str(ids[1])]['kp_raw'][0],
                                  'label': 'ttest(' + 'video_' + str(ids[0]) + ',' + 'video_' + str(ids[1]) + ')',
                                  'paired': True},
                                 {'signal_1': df.loc['video_' + str(ids[0])]['kp_raw'][0],  # 0 and 2 = between
                                  'signal_2': df.loc['video_' + str(ids[2])]['kp_raw'][0],
                                  'label': 'ttest(' + 'video_' + str(ids[0]) + ',' + 'video_' + str(ids[2]) + ')',
                                  'paired': True},
                                 {'signal_1': df.loc['video_' + str(ids[1])]['kp_raw'][0],  # 1 and 2 = between
                                  'signal_2': df.loc['video_' + str(ids[2])]['kp_raw'][0],
                                  'label': 'ttest(' + 'video_' + str(ids[1]) + ',' + 'video_' + str(ids[2]) + ')',
                                  'paired': True}]
                # prepare signals to compare with ANOVA
                # todo: signals for ANOVA
                anova_signals = [{'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                                  'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                                  'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                                  'label': 'anova(0, 1, 2)'},
                                 {'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                                  'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                                  'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                                  'label': 'anova(0, 2, 3)'},
                                 {'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                                  'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                                  'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                                  'label': 'anova(1, 2, 3)'}]
                # plot keypress data and slider questions
                analysis.plot_kp_slider_videos(df,
                                               y=['space', 'estimate'],
                                               # hardcode based on the longest stimulus
                                               xaxis_kp_range=[0, 20],
                                               # hardcode based on the highest recorded value
                                               yaxis_kp_range=[0, 20],
                                               events=events,
                                               events_width=1,
                                               events_dash='dot',
                                               events_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                               events_annotations_font_size=12,
                                               events_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                               yaxis_slider_title=None,
                                               show_text_labels=True,
                                               stacked=False,
                                               yaxis_slider_show=False,
                                               font_size=16,
                                               legend_x=0.71,
                                               legend_y=1.0,
                                               ttest_signals=ttest_signals,
                                               ttest_marker='circle',
                                               ttest_marker_size=3,
                                               ttest_marker_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                               ttest_annotations_font_size=10,
                                               ttest_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                               anova_signals=anova_signals,
                                               anova_marker='cross',
                                               anova_marker_size=3,
                                               anova_marker_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                               anova_annotations_font_size=10,
                                               anova_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                               name_file='kp_videos_sliders_'+','.join([str(i) for i in ids]),
                                               fig_save_width=1600,   # preserve ratio 225x152
                                               fig_save_height=1080,  # preserve ratio 225x152
                                               save_file=True,
                                               save_final=dc.common.get_configs('save_figures'))
            # keypresses of all videos individually
            analysis.plot_kp_videos(mapping,
                                    show_menu=False,
                                    save_file=True,
                                    save_final=dc.common.get_configs('save_figures'))
            # keypress based on the type of distance
            # prepare pairs of signals to compare with ttest
            # todo: @Giovanni, check
            ttest_signals = [{'signal_1': dc.common.vertical_sum(mapping.loc[mapping['distance'] == '0.8 m']['kp_raw'][0]),  # 0.8 m vs B1.6 m # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['distance'] == '1.6 m']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Bike laser projection)',
                              'paired': True},
                             {'signal_1': dc.common.vertical_sum(mapping.loc[mapping['distance'] == '0.8 m']['kp_raw'][0]),  # 0.8 m vs 2.4 m  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['distance'] == '2.4 m']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Vertical sign)',
                              'paired': True},
                             {'signal_1': dc.common.vertical_sum(mapping.loc[mapping['distance'] == '1.6 m']['kp_raw'][0]),  # 1.6 m vs 2.4 m  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['distance'] == '2.4 m']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Vertical sign)',
                              'paired': True}]
            # prepare signals to compare with ANOVA
            # todo: signals for ANOVA
            anova_signals = [{'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                              'label': 'anova(0, 1, 2)'},
                             {'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                              'label': 'anova(0, 2, 3)'},
                             {'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                              'label': 'anova(1, 2, 3)'}]
            analysis.plot_kp_variable(mapping,
                                      'distance',
                                      # custom labels for slider questions in the legend
                                      y_legend=['0.8 m', '1.6 m', '2.4 m'],
                                      font_size=16,
                                      legend_x=0.9,
                                      legend_y=1.0,
                                      show_menu=False,
                                      show_title=False,
                                      # hardcode based on the longest stimulus
                                      xaxis_range=[0, 20],
                                      # hardcode based on the highest recorded value
                                      yaxis_range=[0, 20],
                                      events=events,
                                      events_width=1,
                                      events_dash='dot',
                                      events_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      events_annotations_font_size=12,
                                      events_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      ttest_signals=ttest_signals,
                                      ttest_marker='circle',
                                      ttest_marker_size=3,
                                      ttest_marker_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      ttest_annotations_font_size=10,
                                      ttest_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      anova_signals=anova_signals,
                                      anova_marker='cross',
                                      anova_marker_size=3,
                                      anova_marker_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      anova_annotations_font_size=10,
                                      anova_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      save_file=True,
                                      save_final=dc.common.get_configs('save_figures'))
            # keypress based on the type of interaction
            # prepare pairs of signals to compare with ttest
            ttest_signals = [{'signal_1': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'control']['kp_raw'][0]),  # Control vs Bike laser projection  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'bike_laser_projection']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Bike laser projection)',
                              'paired': True},
                             {'signal_1': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'control']['kp_raw'][0]),  # Control vs Vertical sign  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'vertical_sign']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Vertical sign)',
                              'paired': True},
                             {'signal_1': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'control']['kp_raw'][0]),  # Control vs Danish sign  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'danish_sign']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Danish sign)',
                              'paired': True},
                             {'signal_1': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'control']['kp_raw'][0]),  # Control vs Car laser projection  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'car_laser_projection']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Car laser projection)',
                              'paired': True},
                             {'signal_1': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'control']['kp_raw'][0]),  # Control vs Unprotected cycling path  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'unprotected_cycling_path']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, Unprotected cycling path)',
                              'paired': True},
                             {'signal_1': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'control']['kp_raw'][0]),  # Control vs No road markings  # noqa: E501
                              'signal_2': dc.common.vertical_sum(mapping.loc[mapping['interaction'] == 'no_road_markings']['kp_raw'][0]),  # noqa: E501
                              'label': 'ttest(Control, No road markings)',
                              'paired': True}]
            # prepare signals to compare with ANOVA
            # todo: signals for ANOVA
            anova_signals = [{'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                              'label': 'anova(0, 1, 2)'},
                             {'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                              'label': 'anova(0, 2, 3)'},
                             {'signal_1': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_2': df.loc['video_' + str(ids[0])]['kp'],
                              'signal_3': df.loc['video_' + str(ids[0])]['kp'],
                              'label': 'anova(1, 2, 3)'}]
            # todo: check if legend labels are in correct order
            analysis.plot_kp_variable(mapping,
                                      'interaction',
                                      # custom labels for slider questions in the legend
                                      y_legend=['Bike laser projection',
                                                'Vertical sign',
                                                'Danish sign',
                                                'Car laser projection',
                                                'Control',
                                                'Unprotected cycling path',
                                                'No road markings'],
                                      font_size=16,
                                      legend_x=0.9,
                                      legend_y=1.0,
                                      show_menu=False,
                                      show_title=False,
                                      # hardcode based on the longest stimulus
                                      xaxis_range=[0, 20],
                                      # hardcode based on the highest recorded value
                                      yaxis_range=[0, 20],
                                      events=events,
                                      events_width=1,
                                      events_dash='dot',
                                      events_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      events_annotations_font_size=12,
                                      events_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      ttest_signals=ttest_signals,
                                      ttest_marker='circle',
                                      ttest_marker_size=3,
                                      ttest_marker_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      ttest_annotations_font_size=10,
                                      ttest_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      anova_signals=anova_signals,
                                      anova_marker='cross',
                                      anova_marker_size=3,
                                      anova_marker_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      anova_annotations_font_size=10,
                                      anova_annotations_colour='white' if dc.common.get_configs('plotly_template') == 'plotly_dark' else 'black',  # noqa: E501
                                      save_file=True,
                                      save_final=dc.common.get_configs('save_figures'))
        # Visualisation of stimulus data
        if SHOW_OUTPUT_ST:
            # post stimulus questions for all stimuli
            analysis.bar(mapping,
                         y=['space', 'estimate'],
                         stacked=False,
                         show_text_labels=True,
                         pretty_text=True,
                         save_file=True,
                         save_final=dc.common.get_configs('save_figures'))
            # # post-trial questions of all individual stimuli
            # logger.info('Creating bar plots of post-trial questions for groups of stimuli.')
            # for stim in tqdm(range(int(num_stimuli/3))):  # tqdm adds progress bar
            #     # get ids of stimuli that belong to the same group
            #     ids = [stim*3, stim*3 + 1, stim*3 + 2]
            #     df = mapping[mapping['id'].isin(ids)]
            #     analysis.bar(df,
            #                  y=['space', 'estimate'],
            #                  stacked=False,
            #                  show_text_labels=True,
            #                  pretty_text=True,
            #                  save_file=True)
            # logger.info('Creating bar plots of post-trial questions for groups of distance.')
            # for dist in tqdm(range(int(3))):  # tqdm adds progress bar
            #     # get ids of stimuli that belong to the same group
            #     ids = [dist*3, dist*3 + 1, dist*3 + 2]
            #     df = mapping[mapping['id'].isin(ids)]
            #     analysis.bar(df,
            #                  y=['space', 'estimate'],
            #                  stacked=False,
            #                  show_text_labels=True,
            #                  pretty_text=True,
            #                  save_file=True)
            # columns to drop in correlation matrix and scatter matrix
            columns_drop = ['id', 'video_length', 'min_dur', 'max_dur', 'kp', 'kp_raw', 'interaction']
            # set nan to -1
            df = mapping.fillna(-1)
            # create correlation matrix
            analysis.corr_matrix(df,
                                 columns_drop=columns_drop,
                                 save_file=True,
                                 save_final=dc.common.get_configs('save_figures'))
            # create correlation matrix
            analysis.scatter_matrix(df, columns_drop=columns_drop, diagonal_visible=False, save_file=True,
                                    save_final=dc.common.get_configs('save_figures'))
            # end questions - sliders
            df = heroku_data
            # drop na values
            df = df.dropna()
            # convert data from the end post-experiment slider questions to int
            df[['end-slider-0-0',
                'end-slider-1-0',
                'end-slider-2-0',
                'end2-slider-0-0',
                'end2-scenario_number-0']] = df[['end-slider-0-0',
                                                 'end-slider-1-0',
                                                 'end-slider-2-0',
                                                 'end2-slider-0-0',
                                                 'end2-scenario_number-0']].astype(int)
            # print means
            logger.info('Post-experiment question "After experiencing the videos in the experiment, I will change ' +
                        'my attitude towards maintaining a safe overtaking distance from cyclists.": M={}, SD={}.',
                        df.loc[:, 'end-slider-0-0'].mean(),
                        df.loc[:, 'end-slider-0-0'].std())
            logger.info('Post-experiment question "I felt safe while overtaking the cyclist in the videos.": M={}, ' +
                        'SD={}.',
                        df.loc[:, 'end-slider-1-0'].mean(),
                        df.loc[:, 'end-slider-1-0'].std())
            logger.info('Post-experiment question "Based on my experience, I support the introduction of the ' +
                        'technology used in the scenarios on real roads.": M={}, SD={}.',
                        df.loc[:, 'end-slider-2-0'].mean(),
                        df.loc[:, 'end-slider-2-0'].std())
            logger.info('Post-experiment question "I experienced a high level of stress during all scenarios.": ' +
                        'M={}, SD={}.',
                        df.loc[:, 'end2-slider-0-0'].mean(),
                        df.loc[:, 'end2-slider-0-0'].std())
            # histogram for 3 slider questions
            analysis.hist(df,
                          x=df.columns[df.columns.to_series().str.contains('end-slider-')],
                          nbins=5,
                          pretty_text=True,
                          save_file=True,
                          save_final=dc.common.get_configs('save_figures'))
            # histogram for the amount of stress
            analysis.hist(df,
                          x=df.columns[df.columns.to_series().str.contains('end2-slider-0-0')],
                          nbins=5,
                          pretty_text=True,
                          xaxis_title='I experienced a high level of stress during all scenarios.',
                          save_file=True,
                          save_final=dc.common.get_configs('save_figures'))
            # histogram for the number of scenario
            analysis.hist(df,
                          x=df.columns[df.columns.to_series().str.contains('end2-scenario_number-0')],
                          nbins=7,
                          pretty_text=True,
                          xaxis_title='Which scenario was most helpful in choosing the overtaking distance from ' +
                                      'cyclists?',
                          save_file=True,
                          save_final=dc.common.get_configs('save_figures'))
            # stimulus duration
            analysis.hist(heroku_data,
                          x=heroku_data.columns[heroku_data.columns.to_series().str.contains('-dur')],
                          nbins=100,
                          pretty_text=True,
                          save_file=True,
                          save_final=dc.common.get_configs('save_figures'))
            # mapping to convert likert values to numeric
            likert_mapping = {'Strongly disagree': 1,
                              'Disagree': 2,
                              'Neither disagree nor agree': 3,
                              'Agree': 4,
                              'Strongly agree': 5}
            # # questions before and after
            # df = all_data
            # df['driving_alongside_ad'] = df['driving_alongside_ad'].map(likert_mapping)
            # df['driving_in_ad'] = df['driving_in_ad'].map(likert_mapping)
            # analysis.scatter(df,
            #                  x='driving_alongside_ad',
            #                  y='end-slider-0-0',
            #                  xaxis_title='Before',
            #                  yaxis_title='After',
            #                  pretty_text=True,
            #                  save_file=True)
            # analysis.scatter(df,
            #                  x='driving_in_ad',
            #                  y='end-slider-1-0',
            #                  xaxis_title='Before',
            #                  yaxis_title='After',
            #                  pretty_text=True,
            #                  save_file=True)
        # Visualisation of data about participants
        if SHOW_OUTPUT_PP:
            # time of participation
            df = appen_data
            df['country'] = df['country'].fillna('NaN')
            df['time'] = df['time'] / 60.0  # convert to min
            analysis.hist(df,
                          x=['time'],
                          color='country',
                          pretty_text=True,
                          save_file=True,
                          save_final=dc.common.get_configs('save_figures'))
            # histogram for driving frequency
            analysis.hist(appen_data,
                          x=['driving_freq'],
                          pretty_text=True,
                          save_file=True,
                          save_final=dc.common.get_configs('save_figures'))
            # histogram for cycling frequency
            analysis.hist(appen_data,
                          x=['cycling_freq'],
                          pretty_text=True,
                          save_file=True,
                          save_final=dc.common.get_configs('save_figures'))
            # map of participants
            analysis.map(countries_data,
                         color='counts',
                         save_file=True,
                         save_final=dc.common.get_configs('save_figures'))
            # map of mean age per country
            analysis.map(countries_data,
                         color='age',
                         save_file=True,
                         save_final=dc.common.get_configs('save_figures'))
            # map of gender per country
            analysis.map(countries_data,
                         color='gender',
                         save_file=True,
                         save_final=dc.common.get_configs('save_figures'))
            # map of year of obtaining license per country
            analysis.map(countries_data,
                         color='year_license',
                         save_file=True,
                         save_final=dc.common.get_configs('save_figures'))
        # Visualisation of eye tracking data
        if SHOW_OUTPUT_ET:
            # create eye gaze visualisations for all videos
            logger.info('Producing visualisations of eye gaze data for {} stimuli.',
                        dc.common.get_configs('num_stimuli'))
            if dc.common.get_configs('Combined_animation') == 1:
                num_anim = 21
                logger.info('Animation is set to combined animations of all for scenarios in one figure')
            else:
                num_anim = dc.common.get_configs('num_stimuli')
                logger.info('Animation is set to single stimuli animations in one figure')
            # source video/stimulus for a given individual.
            for id_video in tqdm(range(0, num_anim)):
                logger.info('Producing visualisations of eye gaze data for stimulus {}.', id_video)
                # Deconstruct the source video into its individual frames.
                stim_path = os.path.join(dc.settings.output_dir, 'frames')
                # To allow for overlaying the heatmap for each frame later on.
                analysis.save_all_frames(heroku_data, mapping, id_video=id_video, t='video_length')
                # construct the gazes lines just as an example for how
                # that looks compared to the heatmap.

                # analysis.create_gazes(heroku_data,
                #                       x='video_'+str(id_video)+'-x-0',
                #                       y='video_'+str(id_video)+'-y-0',

                #                       # pp='R51701252541887JF46247X',
                #                       id_video=id_video,
                #                       save_file=True)
                # Construct heatmap over each video frame previously created
                # from the source video.
                # create histogram for stimulus`

                # analysis.create_histogram(stim_path,
                #                   points[id_video],
                #                   id_video=id_video,
                #                   density_coef=20,
                #                   save_file=True)
                # create animation for stimulus
                points_process = {}
                points_process1 = {}
                points_process2 = {}
                points_process3 = {}
                # determin amount of points in duration for video_id
                dur = mapping.iloc[id_video]['video_length']
                hm_resolution_range = int(50000 / dc.common.get_configs('hm_resolution'))
                # To create animation for scenario 1,2,3 & 4 in the
                # same animation extract for all senarios.
                # for individual animations or scenario
                dur = heroku_data['video_'+str(id_video)+'-dur-0'].tolist()
                dur = [x for x in dur if str(x) != 'nan']
                dur = int(round(mean(dur) / 1000) * 1000)
                hm_resolution_range = int(50000 / dc.common.get_configs('hm_resolution'))
                # for individual stim
                for points_dur in range(0, hm_resolution_range, 1):
                    try:
                        points_process[points_dur] = points_duration[points_dur][id_video]
                    except KeyError:
                        break
                # check if animations is set for combined
                if dc.common.get_configs('Combined_animation') == 1:
                    # Scenario 2
                    for points_dur in range(0, hm_resolution_range, 1):
                        try:
                            points_process1[points_dur] = points_duration[points_dur][id_video + 21]
                        except KeyError:
                            break
                    # Scenario 3
                    for points_dur in range(0, hm_resolution_range, 1):
                        try:
                            points_process2[points_dur] = points_duration[points_dur][id_video + 42]
                        except KeyError:
                            break
                    # Scenario 4
                    for points_dur in range(0, hm_resolution_range, 1):
                        try:
                            points_process3[points_dur] = points_duration[points_dur][id_video + 63]
                        except KeyError:
                            break
                analysis.create_animation(heroku_data,
                                          mapping,
                                          stim_path,
                                          id_video,
                                          points_process,
                                          points_process1,
                                          points_process2,
                                          points_process3,
                                          t='video_length',
                                          save_anim=True,
                                          save_frames=True)
                # analysis.create_heatmap(heroku_data,
                #                         x='video_'+str(id_video)+'-x-0',
                #                         y='video_'+str(id_video)+'-y-0',
                #                         pp='R51701252541887JF46247X',
                #                         id_video=id_video,
                #                         type_heatmap='contourf',
                #                         add_corners=True,
                #                         save_file=True)
                # # Animate the kp for given source video.
                # analysis.plot_kp_animate(mapping,
                #                          'video_'+str(id_video),
                #                          conf_interval=0.95)
                #
                # # Create an animation from individual frames
                # #
                # analysis.create_animation(heroku_data,
                #                           x='video_'+str(id_video)+'-x-0',
                #                           y='video_'+str(id_video)+'-y-0',
                #                           t='video_'+str(id_video)+'-t-0',
                #                           pp='R51701252541887JF46247X',
                #                           id_video=id_video,
                #                           save_anim=True,
                #                           save_frames=True)
                # # remove temp folder with frames
                # shutil.rmtree(os.path.join(dc.settings.output_dir, 'frames'))
                # Creating a for loop that makes an eye gazes/heatmap for every
                # create animation for stimulus
                # analysis.scatter_mult(mapping[mapping['avg_person'] != ''],
                #                       x=['avg_object', 'avg_person', 'avg_car'],
                #                       y='avg_kp',
                #                       trendline='ols',
                #                       xaxis_title='Object count',
                #                       yaxis_title='Mean keypresses (%)',
                #                       marginal_y=None,
                #                       marginal_x='rug',
                #                       save_file=True)
                # todo: add comment with description
                analysis.scatter_mult(heroku_data,
                                      x=['video_0-x-0', 'video_1-x-0'],
                                      y='video_0-y-0',
                                      color='browser_major_version',
                                      pretty_text=True,
                                      save_file=True)
                # Create individual scatter plot for given video and participant.
                # analysis.scatter_et(heroku_data,
                #                     x='video_0-x-0',
                #                     y='video_0-y-0',
                #                     t='video_0-t-0',
                #                     pp='R51701252541887JF46247X',
                #                     id_video='video_0',
                #                     pretty_text=True,
                #                     save_file=True)
                # Create individual heatmap for given video and participant.
                # analysis.heatmap(heroku_data,
                #                     x='video_0-x-0',
                #                     y='video_0-y-0',
                #                     t='video_0-t-0',
                #                     pp='R51701252541887JF46247X',
                #                     id_video='video_0',
                #                     pretty_text=True,self.event_discription
                #                     save_file=True)
                # stitch animations into 1 long videos
                analysis.create_animation_all_stimuli(num_stimuli)
        # collect figure objects
        figures = [manager.canvas.figure
                   for manager in
                   matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
        # show figures, if any
        if figures:
            plt.show()


