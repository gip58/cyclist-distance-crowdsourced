# by Giovanni Sapienza () and Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>


import dcycl as dc

logger = dc.CustomLogger(__name__)  # use custom logger


class Simulator(object):
    """Working with data from simulator.
    """
    def __init__(self,
                 files_data: list,
                 save_p: bool,
                 load_p: bool,
                 save_csv: bool):
        # files with raw data
        self.files_data = files_data # Simulator/path
        # save data as pickle file
        self.save_p = save_p
        # load data as pickle file
        self.load_p = load_p
        # save data as csv file
        self.save_csv = save_csv

    def analysis():
        """
        average speed per scenario 
        average distance per scenario - averaged minimum distance
        bar chart for preferences
        average overtaking distance over time + t-test
        """

    def read_data(self, filter_data=True, clean_data=True):
        """Read data into an attribute.

        Args:
            filter_data (bool, optional): flag for filtering data.

        Returns:
            dataframe: updated dataframe.
        """
        # load data
        if self.load_p:
            df = dc.common.load_from_p(self.file_p, 'simulaor data')
        # process data
        else:
            # read files with heroku data one by one
            data_list = []
            data_dict = {}  # dictionary with data
            for file in self.files_data:
                logger.info('Reading heroku data from {}.', file)
                f = open(file, 'r')
                # add data from the file to the dictionary
                data_list += f.readlines()
                f.close()
            # hold info on previous row for worker
            prev_row_info = pd.DataFrame(columns=['worker_code', 'time_elapsed'])
            prev_row_info.set_index('worker_code', inplace=True)
            # read rows in data
            for row in tqdm(data_list):  # tqdm adds progress bar
                # use dict to store data
                dict_row = {}
                # load data from a single row into a list
                list_row = json.loads(row)
                # last found stimulus
                stim_name = ''
                # trial last found stimulus
                stim_trial = -1
                # last time_elapsed for logging duration of trial and stimulus
                elapsed_l = 0
                elapsed_l_stim = 0
                # record worker_code in the row. assuming that each row has at least one worker_code
                worker_code = [d['worker_code'] for d in list_row['data'] if 'worker_code' in d][0]
                # go over cells in the row with data
                for data_cell in list_row['data']:
                    # extract meta info form the call
                    for key in self.meta_keys:
                        if key in data_cell.keys():
                            # piece of meta data found, update dictionary
                            dict_row[key] = data_cell[key]
                            if key == 'worker_code':
                                logger.debug('{}: working with row with data.', data_cell['worker_code'])
                    # check if stimulus data is present
                    if 'stimulus' in data_cell.keys():
                        # record last timestamp before video
                        if 'black_frame.png' in data_cell['stimulus']:
                            # record timestamp at the black frame to compute
                            # the length of the stimulus
                            if 'time_elapsed' in data_cell.keys():
                                elapsed_l_stim = float(data_cell['time_elapsed'])
                        # extract name of stimulus after last slash
                        # list of stimuli. use 1st
                        if isinstance(data_cell['stimulus'], list):
                            stim_no_path = data_cell['stimulus'][0].rsplit('/', 1)[-1]
                        # single stimulus
                        else:
                            stim_no_path = data_cell['stimulus'].rsplit('/', 1)[-1]
                        # remove extension
                        stim_no_path = os.path.splitext(stim_no_path)[0]
                        # skip is videos from instructions
                        if 'video_test_' in stim_no_path:
                            continue
                        # Check if it is a block with stimulus and not an
                        # instructions block
                        if (dc.common.search_dict(self.prefixes, stim_no_path)
                                is not None):
                            # stimulus is found
                            logger.debug('Found stimulus {}.', stim_no_path)
                            if self.prefixes['stimulus'] in stim_no_path:
                                # Record that stimulus was detected for the
                                # cells to follow
                                stim_name = stim_no_path
                                # record trial of stimulus
                                stim_trial = data_cell['trial_index']
                                # add trial duration
                                if 'time_elapsed' in data_cell.keys():
                                    # positive time elapsed from last cell
                                    if elapsed_l_stim:
                                        time = elapsed_l_stim
                                    # non-positive time elapsed. use value from
                                    # the known cell for worker
                                    else:
                                        time = prev_row_info.loc[worker_code, 'time_elapsed']
                                    # calculate duration
                                    dur = float(data_cell['time_elapsed']) - time
                                    if stim_name + '-dur' not in dict_row.keys() and dur > 0:
                                        # first value
                                        dict_row[stim_name + '-dur'] = dur
                    # keypresses
                    if 'rts' in data_cell.keys() and stim_name != '':
                        # record given keypresses
                        responses = data_cell['rts']
                        logger.debug('Found {} points in keypress data.', len(responses))
                        # extract pressed keys and rt values
                        key = [point['key'] for point in responses]
                        rt = [point['rt'] for point in responses]
                        # check if values were recorded previously
                        if stim_name + '-key' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-key'] = key
                        else:
                            # previous values found
                            dict_row[stim_name + '-key'].extend(key)
                        # check if values were recorded previously
                        if stim_name + '-rt' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-rt'] = rt
                        else:
                            # previous values found
                            dict_row[stim_name + '-rt'].extend(rt)
                    # eye tracking data
                    if 'webgazer_data' in data_cell.keys() and stim_name != '':
                        # record eye tracking data
                        et_data = data_cell['webgazer_data']
                        logger.debug('Found {} points in eye tracking data.', len(et_data))
                        # extract x,y,t values
                        x = [point['x'] for point in et_data]
                        y = [point['y'] for point in et_data]
                        t = [point['t'] for point in et_data]
                        # check if values not already recorded
                        if stim_name + '-x' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-x'] = x
                        else:
                            # previous values found
                            dict_row[stim_name + '-x'].extend(x)
                        # check if values not already recorded
                        if stim_name + '-y' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-y'] = y
                        else:
                            # previous values found
                            dict_row[stim_name + '-y'].extend(y)
                        # check if values not already recorded
                        if stim_name + '-t' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-t'] = t
                        else:
                            # previous values found
                            dict_row[stim_name + '-t'].extend(t)
                    # questions after stimulus
                    if ('response' in data_cell.keys() and stim_name != '' and
                       data_cell['response'] is not None):
                        # check if it is not dictionary
                        if 'slider-0' not in data_cell['response']:
                            continue
                        # record given answers
                        responses = data_cell['response']
                        logger.debug('Found responses to questions {}.', responses)
                        # unpack questions and answers
                        questions = []
                        answers = []
                        for key, value in responses.items():
                            questions.append(key)
                            answers.append(int(value))
                        # check if values were recorded previously
                        if stim_name + '-qs' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-qs'] = questions
                        else:
                            # previous values found
                            dict_row[stim_name + '-qs'].extend(questions)
                        # Check if time spent values were recorded
                        # previously
                        if stim_name + '-as' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-as'] = answers
                        else:
                            # previous values found
                            dict_row[stim_name + '-as'].extend(answers)
                    # browser interaction events
                    if 'interactions' in data_cell.keys() and stim_name != '':
                        interactions = data_cell['interactions']
                        logger.debug('Found {} browser interactions.', len(interactions))
                        # extract events and timestamps
                        event = []
                        time = []
                        for interation in interactions:
                            if interation['trial'] == stim_trial:
                                event.append(interation['event'])
                                time.append(interation['time'])
                        # Check if inputted values were recorded previously
                        if stim_name + '-event' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-event'] = event
                        else:
                            # previous values found
                            dict_row[stim_name + '-event'].extend(event)
                        # check if values were recorded previously
                        if stim_name + '-time' not in dict_row.keys():
                            # first value
                            dict_row[stim_name + '-time'] = time
                        else:
                            # previous values found
                            dict_row[stim_name + '-time'].extend(time)
                    # sliders after experiment
                    if ('response' in data_cell.keys() and stim_name == '' and
                       data_cell['response'] is not None):
                        # check if it is not post-trial data
                        if 'slider-5' not in data_cell['response']:
                            continue
                        # record given keypresses
                        responses_end = data_cell['response']
                        logger.debug('Found responses to the questions in ' +
                                     'the end {}.', responses_end)
                        for key, value in responses_end.items():
                            # check if values not already recorded
                            if stim_name + 'end-' + key not in dict_row.keys():
                                # first value
                                dict_row['end-' + key] = value
                            else:
                                # previous values found
                                dict_row['end-' + key].extend(value)
                    # record last time_elapsed
                    if 'time_elapsed' in data_cell.keys():
                        elapsed_l = float(data_cell['time_elapsed'])
                # update last time_elapsed for worker
                prev_row_info.loc[dict_row['worker_code'], 'time_elapsed'] = elapsed_l
                # worker_code was encountered before
                if dict_row['worker_code'] in data_dict.keys():
                    # iterate over items in the data dictionary
                    for key, value in dict_row.items():
                        # worker_code does not need to be added
                        if key in self.meta_keys:
                            data_dict[dict_row['worker_code']][key] = value
                            continue
                        # new value
                        if key + '-0' not in data_dict[dict_row['worker_code']].keys():
                            data_dict[dict_row['worker_code']][key + '-0'] = value
                        # update old value
                        else:
                            # traverse repetition ids until get new repetition
                            for rep in range(0, self.num_repeat):
                                # build new key with id of repetition
                                new_key = key + '-' + str(rep)
                                if new_key not in data_dict[dict_row['worker_code']].keys():
                                    data_dict[dict_row['worker_code']][new_key] = value
                                    break
                # worker_code is encountered for the first time
                else:
                    # iterate over items in the data dictionary and add -0
                    for key, value in list(dict_row.items()):
                        # worker_code does not need to be added
                        if key in self.meta_keys:
                            continue
                        # new value
                        dict_row[key + '-0'] = dict_row.pop(key)
                    # add row of data
                    data_dict[dict_row['worker_code']] = dict_row
            # turn into pandas dataframe
            df = pd.DataFrame(data_dict)
            df = df.transpose()
            # report people that attempted study
            unique_worker_codes = df['worker_code'].drop_duplicates()
            logger.info('People who attempted to participate: {}', unique_worker_codes.shape[0])
            # filter data
            if filter_data:
                df = self.filter_data(df)
            # sort columns alphabetically
            df = df.reindex(sorted(df.columns), axis=1)
            # move worker_code to the front
            worker_code_col = df['worker_code']
            df.drop(labels=['worker_code'], axis=1, inplace=True)
            df.insert(0, 'worker_code', worker_code_col)
        # save to pickle
        if self.save_p:
            dc.common.save_to_p(self.file_p, df, 'heroku data')
        # save to csv
        if self.save_csv:
            # build path
            if not os.path.exists(dc.settings.output_dir):
                os.makedirs(dc.settings.output_dir)
            # save to file
            df.to_csv(os.path.join(dc.settings.output_dir, self.file_data_csv), index=False)
            logger.info('Saved heroku data to csv file {}', self.file_data_csv + '.csv')
        # update attribute
        self.heroku_data = df
        # return df with data
        return df

    def filter_data(self, df):
        pass
