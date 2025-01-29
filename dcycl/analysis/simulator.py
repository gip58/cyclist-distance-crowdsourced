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
        self.files_data = files_data
        # save data as pickle file
        self.save_p = save_p
        # load data as pickle file
        self.load_p = load_p
        # save data as csv file
        self.save_csv = save_csv

    def read_data(self, filter_data=True, clean_data=True):
        pass

    def filter_data(self, df):
        pass
