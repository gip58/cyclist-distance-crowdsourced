import os
import pandas as pd
import dcycl as dc

dc.logs(show_level="info", show_color=True)
logger = dc.CustomLogger(__name__)  # use custom logger


class Simulator(object):
    """Working with data from simulator."""

    df = pd.DataFrame()

    scenario_names = {
        1: "Laser projection",
        2: "Vertical signage",
        3: "Road markings",
        4: "Car projection system",
        5: "Centre line and side-line markings",
        6: "Unprotected cycling path",
        7: "No road markings",
        "Scenario_1": "Laser projection",
        "Scenario_2": "Vertical signage",
        "Scenario_3": "Road markings",
        "Scenario_4": "Car projection system",
        "Scenario_5": "Centre line and side-line markings",
        "Scenario_6": "Unprotected cycling path",
        "Scenario_7": "No road markings",
    }

    # set template for plotly output
    template = ""

    def __init__(self, files_simulator: str, save_p: bool, load_p: bool, save_csv: bool):
        # files with raw data
        self.files_simulator = files_simulator
        # save data as pickle file
        self.save_p = save_p
        # load data as pickle file
        self.load_p = load_p
        # save data as csv file
        self.save_csv = save_csv
        # folder for saving figures
        self.folder_figures = 'figures'

        self.template = dc.common.get_configs("plotly_template")

    def read_data(self, filter_data=True, clean_data=True):
        """Read data into an attribute.

        Args:
            filter_data (bool, optional): flag for filtering data.

        Returns:
            dataframe: updated dataframe.
        """

        scenario_files = os.listdir(os.path.join(self.files_simulator, "data"))

        for scenario in scenario_files:
            # skip .DS_Store file
            if scenario == ".DS_Store":
                continue
            scenario_path = os.path.join(os.path.join(self.files_simulator, "data"), scenario)
            csv_files = [f for f in os.listdir(scenario_path) if f.endswith(".csv")]
            for participant_id, csv_file in enumerate(csv_files):
                file_path = os.path.join(scenario_path, csv_file)
                df_scenario = pd.read_csv(file_path)
                df_scenario["ScenarioID"] = int(scenario[-1])  # Add scenario label
                df_scenario["Scenario"] = self.scenario_names[scenario]
                df_scenario["Participant"] = participant_id
                self.df = pd.concat([self.df, df_scenario])

        self.df.columns = self.df.columns.str.strip()

        # Remove the first 4 seconds (due to countdown)
        self.df = self.df[self.df["Time"] >= 4]

        return self.df

    def filter_data(self, df):
        pass

    def get_preferences(self):
        raw_data_file = os.path.join(self.files_simulator, "simulator_questionnaire_results.csv")
        df = pd.read_csv(raw_data_file)
        preferred_col = "Which of the seven scenarios, featuring various technologies such as road markings or laser projections, was most helpful in accurately determining the distance between the car and the cyclist?"
        counts = df[preferred_col].value_counts()
        logger.info("Preference counts per scenario:")
        for scenario, count in counts.items():
            logger.info(f"{scenario}: {count}")
