# by Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>
import pandas as pd
import numpy as np
import os
from collections import Counter
from pycountry_convert import country_alpha2_to_country_name, country_name_to_country_alpha3
import dcycl as dc

logger = dc.CustomLogger(__name__)  # use custom logger


class Appen:
    # pandas dataframe with extracted data
    appen_data = pd.DataFrame()
    # pandas dataframe with data per country
    countries_data = pd.DataFrame()
    # pickle file for saving data
    file_p = 'appen_data.p'
    # csv file for saving data
    file_csv = 'appen_data.csv'
    # csv file for saving country data
    file_country_csv = 'country_data.csv'
    # csv file for saving list of cheaters
    file_cheaters_csv = 'cheaters.csv'
    # mapping between appen column names and readable names
    columns_mapping = {'_started_at': 'start',
                       '_created_at': 'end',
                       'about_how_many_kilometers_miles_did_you_drive_in_the_last_12_months': 'milage',
                       'are_you_aware_of_any_laws_or_guidelines_in_your_country_or_within_the_eu_that_specify_the_minimum_distance_a_car_should_maintain_when_overtaking_a_cyclist': 'cycling_distance',  # noqa: E501
                       'as_a_cyclist_what_are_your_biggest_concerns_when_vehicles_overtake_you_on_the_road': 'cycling_concerns',  # noqa: E501
                       'at_which_age_did_you_obtain_your_first_license_for_driving_a_car': 'year_license',
                       'do_you_change_your_behaviour_when_driving_in_areas_with_many_ciclysts_if_so_how': 'change_behaviour',  # noqa: E501
                       'have_you_read_and_understood_the_above_instructions': 'instructions',
                       'do_you_consent_to_participate_in_this_study_in_the_way_that_is_described_in_the_information_shown_above': 'consent',  # noqa: E501
                       'do_you_hold_a_valid_drivers_license': 'valid_license',
                       'do_you_think_the_current_laws_or_guidelines_are_sufficient_to_ensure_cyclists_safety_why_or_why_not': 'cycling_laws',  # noqa: E501
                       'from_which_country_is_the_driving_license_issued': 'license_country',  # noqa: E501
                       'have_you_ever_felt_pressured_by_other_drivers_or_traffic_conditions_to_overtake_a_cyclist_more_closely_than_you_would_prefer': 'cycling_pressure',  # noqa: E501
                       'have_you_ever_had_a_near_accident_or_an_accident_due_to_a_vehicle_overtaking_you_too_close_how_did_that_experience_impact_your_sense_of_safety_while_cycling': 'cycling_overtake',  # noqa: E501
                       'how_do_you_feel_about_sharing_the_road_with_cyclists_do_you_think_there_should_be_more_infrastructure_dedicated_to_cyclists_such_as_cycling_lanes': 'cycling_infrastructure',  # noqa: E501
                       'if_you_cycle_do_you_alter_your_route_or_timing_to_avoid_areas_where_drivers_tend_to_pass_too_closely': 'cycling_route',  # noqa: E501
                       'how_many_accidents_were_you_involved_in_when_driving_a_car_in_the_last_3_years_please_include_all_accidents_regardless_of_how_they_were_caused_how_slight_they_were_or_where_they_happened': 'accidents',  # noqa: E501
                       'becoming_angered_by_a_particular_type_of_driver_and_indicate_your_hostility_by_whatever_means_you_can': 'dbq1_anger',  # noqa: E501
                       'disregarding_the_speed_limit_on_a_motorway': 'dbq2_speed_motorway',
                       'disregarding_the_speed_limit_on_a_residential_road': 'dbq3_speed_residential',
                       'driving_so_close_to_the_car_in_front_that_it_would_be_difficult_to_stop_in_an_emergency': 'dbq4_headway',  # noqa: E501
                       'racing_away_from_traffic_lights_with_the_intention_of_beating_the_driver_next_to_you': 'dbq5_traffic_lights',  # noqa: E501
                       'sounding_your_horn_to_indicate_your_annoyance_with_another_road_user': 'dbq6_horn',
                       'using_a_phone_in_your_hands_while_driving': 'dbq7_mobile',
                       'doing_my_best_not_to_be_obstacle_for_other_drivers': 'dbq8_others',
                       'if_you_answered_other_in_the_previous_question_please_describe_your_experiences_below': 'experiences_other',  # noqa: E501
                       'if_you_answered_other_in_the_previous_question_please_describe_your_input_device_below': 'device_other',  # noqa: E501
                       'in_which_type_of_place_are_you_located_now': 'place',
                       'if_you_answered_other_in_the_previous_question_please_describe_the_place_where_you_are_located_now_below': 'place_other',  # noqa: E501
                       'on_average_how_often_did_you_drive_a_car_in_the_last_12_months': 'driving_freq',
                       'on_average_how_often_did_you_drive_a_bicycle_in_the_last_12_months': 'cycling_freq',
                       'please_provide_an_estimate_of_what_you_believe_the_minimum_distance_for_overtaking_a_cyclist_should_be_in_metres': 'cycling_overtake_m',  # noqa: E501
                       'please_provide_any_suggestions_that_could_help_engineers_to_build_safe_and_enjoyable_interaction_between_all_road_user': 'suggestions_ad',  # noqa: E501
                       'type_the_code_that_you_received_at_the_end_of_the_experiment': 'worker_code',
                       'what_challenges_have_you_encountered_when_trying_to_maintain_a_safe_distance_from_cyclists_while_driving': 'cycling_challenges',  # noqa: E501
                       'what_factors_influence_your_decision_on_how_much_space_to_leave_when_overtaking_a_cyclist_eg_road_width_speed_traffic_conditions': 'cycling_factors',  # noqa: E501
                       'what_if_anything_would_encourage_you_to_consistently_maintain_a_safe_distance_when_overtaking_cyclists_eg_stricter_laws_better_infrastructure_personal_experiences': 'cycling_encouragement',  # noqa: E501
                       'what_is_your_age': 'age',
                       'what_is_your_gender': 'gender',
                       'when_overtaking_a_cyclist_how_do_you_determine_a_safe_distance': 'cycling_determening',
                       'while_driving_have_you_ever_encountered_a_traffic_situation_where_you_were_required_to_overtake_a_cyclist': 'cycling_required',  # noqa: E501
                       'what_is_the_highest_level_of_education_you_have_completed': 'education',
                       'what_is_your_primary_mode_of_transportation': 'mode_transportation',
                       'which_input_device_are_you_using_now': 'device'}

    def __init__(self,
                 file_data: list,
                 save_p: bool,
                 load_p: bool,
                 save_csv: bool):
        # file with raw data
        self.file_data = file_data
        # save data as pickle file
        self.save_p = save_p
        # load data as pickle file
        self.load_p = load_p
        # save data as csv file
        self.save_csv = save_csv

    def set_data(self, appen_data):
        """Setter for the data object.
        """
        old_shape = self.appen_data.shape  # store old shape for logging
        self.appen_data = appen_data
        logger.info('Updated appen_data. Old shape: {}. New shape: {}.',
                    old_shape,
                    self.appen_data.shape)

    def read_data(self, filter_data=True, clean_data=True):
        """Read data into an attribute.

        Args:
            filter_data (bool, optional): flag for filtering data.
            clean_data (bool, optional): clean data.

        Returns:
            dataframe: udpated dataframe.
        """
        # load data
        if self.load_p:
            df = dc.common.load_from_p(self.file_p, 'appen data')
        # process data
        else:
            logger.info('Reading appen data from {}.', self.file_data)
            # load from csv
            df = pd.read_csv(self.file_data)
            # drop _gold columns
            df = df.drop((x for x in df.columns.tolist() if '_gold' in x), axis=1)
            # replace linebreaks
            df = df.replace('\n', '', regex=True)
            # rename columns to readable names
            df.rename(columns=self.columns_mapping, inplace=True)
            # convert to time
            df['start'] = pd.to_datetime(df['start'])
            df['end'] = pd.to_datetime(df['end'])
            df['time'] = (df['end'] - df['start']) / pd.Timedelta(seconds=1)
            # remove underscores in the beginning of column name
            df.columns = df.columns.str.lstrip('_')
            # clean data
            if clean_data:
                df = self.clean_data(df)
            # filter data
            if filter_data:
                df = self.filter_data(df)
            # mask IDs and IPs
            df = self.mask_ips_ids(df)
            # move worker_code to the front
            worker_code_col = df['worker_code']
            df.drop(labels=['worker_code'], axis=1, inplace=True)
            df.insert(0, 'worker_code', worker_code_col)
        # save to pickle
        if self.save_p:
            dc.common.save_to_p(self.file_p, df, 'appen data')
        # save to csv
        if self.save_csv:
            # replace line breaks to avoid problem with lines spanning over multiple rows
            df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
            # create folder if not present
            if not os.path.exists(df.settings.output_dir):
                os.makedirs(df.settings.output_dir)
            # save to file
            df.to_csv(os.path.join(dc.settings.output_dir, self.file_csv))
            logger.info('Saved appen data to csv file {}', self.file_csv)
        # assign to attribute
        self.appen_data = df
        # return df with data
        return df

    def filter_data(self, df):
        """Filter data based on the following criteria:
            1. People who did not read instructions.
            2. People who did not give consent.
            3. People that are under 18 years of age.
            4. People who completed the study in under 5 min.
            5. People who completed the study from the same IP more than once (the 1st data entry is retained).
            6. People who used the same `worker_code` multiple times.
            7. People with invalid `worker_id`.
        """
        logger.info('Filtering appen data.')
        # people that did not read instructions
        df_1 = df.loc[df['instructions'] == 'no']
        df_1 = df_1.reset_index()
        logger.info('Filter-a1. People who did not read instructions: {}', df_1.shape[0])
        # people that did not give consent
        df_2 = df.loc[df['consent'] == 'no']
        df_2 = df_2.reset_index()
        logger.info('Filter-a2. People who did not give consent: {}', df_2.shape[0])
        # people that are underages
        df_3 = df.loc[df['age'] < 18]
        df_3 = df_3.reset_index()
        logger.info('Filter-a3. People that are under 18 years of age: {}', df_3.shape[0])
        # People that took less than dc.common.get_configs('allowed_min_time')
        # minutes to complete the study
        df_4 = df.loc[df['time'] < dc.common.get_configs('allowed_min_time')]
        df_4 = df_4.reset_index()
        logger.info('Filter-a4. People who completed the study in under ' +
                    str(dc.common.get_configs('allowed_min_time')) +
                    ' sec: {}',
                    df_4.shape[0])
        # people that completed the study from the same IP address
        df_5 = df[df['ip'].duplicated(keep='first')]
        df_5 = df_5.reset_index()
        logger.info('Filter-a5. People who completed the study from the same IP: {}', df_5.shape[0])
        # people that entered the same worker_code more than once
        df_6 = df[df['worker_code'].duplicated(keep='first')]
        df_6 = df_6.reset_index()
        logger.info('Filter-a6. People who used the same worker_code: {}', df_6.shape[0])
        # save to csv
        if self.save_csv:
            df_6.to_csv(os.path.join(dc.settings.output_dir, self.file_cheaters_csv))
            logger.info('Filter-a6. Saved list of cheaters to csv file {}', self.file_cheaters_csv)
        # people with nan for worker_id
        df_7 = df[df['worker_id'].isnull()]
        df_7 = df_7.reset_index()
        logger.info('Filter-a7. People who had not valid worker_id: {}', df_7.shape[0])
        # concatenate dfs with filtered data
        old_size = df.shape[0]
        df_filtered = pd.concat([df_1, df_2, df_3, df_4, df_5, df_6, df_7])
        # check if there are people to filter
        if not df_filtered.empty:
            # drop rows with filtered data
            unique_worker_codes = df_filtered['worker_code'].drop_duplicates()
            df = df[~df['worker_code'].isin(unique_worker_codes)]
            # reset index in dataframe
            df = df.reset_index()
        logger.info('Filtered in total in appen data: {}', old_size - df.shape[0])
        # assign to attribute
        self.appen_data = df
        # return df with data
        return df

    def clean_data(self, df, clean_years=True):
        """Clean data from unexpected values.

        Args:
            df (dataframe): dataframe with data.
            clean_years (bool, optional): clean years question by removing
                                          unrealistic answers.

        Returns:
            dataframe: updated dataframe.
        """
        logger.info('Cleaning appen data.')
        if clean_years:
            # get current number of nans
            nans_before = np.zeros(3, dtype=np.int8)
            nans_before[0] = df['year_license'].isnull().sum()
            nans_before[1] = df['age'].isnull().sum()
            # replace all non-numeric values to nan for questions involving years
            df['year_license'] = df['year_license'].apply(
                lambda x: pd.to_numeric(x, errors='coerce'))
            df['age'] = df['age'].apply(
                lambda x: pd.to_numeric(x, errors='coerce'))
            logger.info('Clean-a1. Replaced {} non-numeric values in columns'
                        + ' year_license, {} non-numeric values in column'
                        + ' age.',
                        df['year_license'].isnull().sum() - nans_before[1],
                        df['age'].isnull().sum() - nans_before[2])
            # replace number of nans
            nans_before[0] = df['year_license'].isnull().sum()
            nans_before[1] = df['age'].isnull().sum()
            # year of obtaining driver's license is assumed to be always < 70
            df.loc[df['year_license'] >= 70] = np.nan
            # age is assumed to be always < 100
            df.loc[df['age'] >= 100] = np.nan
            logger.info('Clean-a2. Cleaned {} values of years in column year_license, {} values in column age.',
                        df['year_license'].isnull().sum() - nans_before[0],
                        df['age'].isnull().sum() - nans_before[1])
        # assign to attribute
        self.appen_data = df
        # return df with data
        return df

    def mask_ips_ids(self, df, mask_ip=True, mask_id=True):
        """Anonymyse IPs and IDs. IDs are anonymised by subtracting the
        given ID from dc.common.get_configs('mask_id').
        """
        # loop through rows of the file
        if mask_ip:
            proc_ips = []  # store masked IP's here
            logger.info('Replacing IPs in appen data.')
        if mask_id:
            proc_ids = []  # store masked ID's here
            logger.info('Replacing IDs in appen data.')
        for i in range(len(df['ip'])):  # loop through ips
            # anonymise IPs
            if mask_ip:
                # IP address
                # new IP
                if not any(d['o'] == df['ip'][i] for d in proc_ips):
                    # mask in format 0.0.0.ID
                    masked_ip = '0.0.0.' + str(len(proc_ips))
                    # record IP as already replaced
                    # o=original; m=masked
                    proc_ips.append({'o': df['ip'][i], 'm': masked_ip})
                    df.at[i, 'ip'] = masked_ip
                    logger.debug('{}: replaced IP {} with {}.',
                                 df['worker_code'][i],
                                 proc_ips[-1]['o'],
                                 proc_ips[-1]['m'])
                else:  # already replaced
                    for item in proc_ips:
                        if item['o'] == df['ip'][i]:

                            # fetch previously used mask for the IP
                            df.at[i, 'ip'] = item['m']
                            logger.debug('{}: replaced repeating IP {} with ' +
                                         '{}.',
                                         df['worker_code'][i],
                                         item['o'],
                                         item['m'])
            # anonymise worker IDs
            if mask_id:
                # new worker ID
                if not any(d['o'] == df['worker_id'][i] for d in proc_ids):
                    # mask in format random_int - worker_id
                    masked_id = (str(dc.common.get_configs('mask_id') -
                                     df['worker_id'][i]))
                    # record IP as already replaced
                    proc_ids.append({'o': df['worker_id'][i],
                                     'm': masked_id})
                    df.at[i, 'worker_id'] = masked_id
                    logger.debug('{}: replaced ID {} with {}.',
                                 df['worker_code'][i],
                                 proc_ids[-1]['o'],
                                 proc_ids[-1]['m'])
                # already replaced
                else:
                    for item in proc_ids:
                        if item['o'] == df['worker_id'][i]:
                            # fetch previously used mask for the ID
                            df.at[i, 'worker_id'] = item['m']
                            logger.debug('{}: replaced repeating ID {} '
                                         + 'with {}.',
                                         df['worker_code'][i],
                                         item['o'],
                                         item['m'])
        # output for checking
        if mask_ip:
            logger.info('Finished replacement of IPs in appen data.')
            logger.info('Unique IPs detected: {}', str(len(proc_ips)))
        if mask_id:
            logger.info('Finished replacement of IDs in appen data.')
            logger.info('Unique IDs detected: {}', str(len(proc_ids)))
        # return dataframe with replaced values
        return df

    def process_countries(self):
        # todo: map textual questions to int
        # df for reassignment of textual values
        df = self.appen_data
        # df for storing counts
        df_counts = pd.DataFrame()
        # get countries and counts of participants
        df_counts['counts'] = df['country'].value_counts()
        # set i_prefer_not_to_respond as nan
        df[df == 'i_prefer_not_to_respond'] = np.nan
        df[df == 'Other'] = np.nan
        # map gender
        di = {'female': 0, 'male': 1}
        df = df.replace({'gender': di})
        # get mean values for countries
        df_country = df.groupby('country').mean(numeric_only=True).reset_index()
        df_country['year_license'] = df.groupby('country').median(numeric_only=True).reset_index()['year_license']
        # assign counts after manipulations
        df_country = df_country.set_index('country', drop=False)
        df_country = df_country.merge(df_counts,
                                      left_index=True,
                                      right_index=True,
                                      how='left')
        # drop not needed columns
        df_country = df_country.drop(columns=['unit_id', 'id'])
        # convert from to 3-letter codes
        df_country['country'] = df_country['country'].apply(lambda x: country_name_to_country_alpha3(country_alpha2_to_country_name(x)))  # noqa: E501
        # assign to attribute
        self.countries_data = df_country
        # save to csv
        if self.save_csv:
            df_country.to_csv(os.path.join(dc.settings.output_dir, self.file_country_csv))
            logger.info('Saved country data to csv file {}', self.file_csv)
        # return df with data
        return df_country

    def show_info(self):
        """Output info for data in object.
        """
        # info on age
        logger.info('Age: mean={:,.2f}, std={:,.2f}.', self.appen_data['age'].mean(), self.appen_data['age'].std())
        # info on gender
        count = Counter(self.appen_data['gender'])
        logger.info('Gender: {}.', count.most_common())
        # info on most represted countries in minutes
        count = Counter(self.appen_data['country'])
        logger.info('Countires: {}.', count.most_common())
        # info on duration in minutes
        logger.info('Time of participation: mean={:,.2f} min, '
                    + 'median={:,.2f} min, std={:,.2f} min.',
                    self.appen_data['time'].mean() / 60,
                    self.appen_data['time'].median() / 60,
                    self.appen_data['time'].std() / 60)
        logger.info('Oldest timestamp={}, newest timestamp={}.',
                    self.appen_data['start'].min(),
                    self.appen_data['start'].max())
