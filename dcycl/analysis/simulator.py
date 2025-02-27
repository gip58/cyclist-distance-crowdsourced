# by Giovanni Sapienza () and Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>


import json
import os

import numpy as np
import pandas as pd
import plotly as py
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import scipy.stats as stats
from scipy.stats import ttest_ind



# import dcycl as dc

# from analysis import Analysis

# logger = dc.CustomLogger(__name__)  # use custom logger


class Simulator(object):
    """Working with data from simulator."""

    df = pd.DataFrame()

    scenario_names = {
        1: "Laser Projection",
        2: "Vertical Signage",
        3: "Road Markings",
        4: "Car Projection System",
        5: "Center Line and Side-Line Markings",
        6: "Unprotected Cycling Path",
        7: "No Road Markings",
        "Scenario_1": "Laser Projection",
        "Scenario_2": "Vertical Signage",
        "Scenario_3": "Road Markings",
        "Scenario_4": "Car Projection System",
        "Scenario_5": "Center Line and Side-Line Markings",
        "Scenario_6": "Unprotected Cycling Path",
        "Scenario_7": "No Road Markings",
    }

    # set template for plotly output
    template = ""

    @staticmethod
    def get_configs(
        entry_name: str,
        config_file_name: str = "config",
        config_default_file_name: str = "default.config",
    ):
        """
        Open the config file and return the requested entry.
        If no config file is found, open default.config.
        """
        # check if config file is updated
        try:
            with open(
                os.path.join(
                    os.path.normpath(os.path.join(os.path.dirname(__file__), "../..")),
                    config_file_name,
                )
            ) as f:
                content = json.load(f)
        except FileNotFoundError:
            with open(
                os.path.join(
                    os.path.normpath(os.path.join(os.path.dirname(__file__), "../..")),
                    config_default_file_name,
                )
            ) as f:
                content = json.load(f)
        return content[entry_name]

    def __init__(self, files_data: str, save_p: bool, load_p: bool, save_csv: bool):
        # files with raw data
        self.files_data = files_data  # Simulator/path
        # save data as pickle file
        self.save_p = save_p
        # load data as pickle file
        self.load_p = load_p
        # save data as csv file
        self.save_csv = save_csv
        # folder for saving figures
        self.folder_figures = Simulator.get_configs("simulator_folder_figures")

        self.template = Simulator.get_configs("plotly_template")




    def plot_preferences(self, save_fig=True):
        # Load global font settings from the config file
        font_family = Simulator.get_configs("font_family")  
        font_size = Simulator.get_configs("font_size")  


        preferences_file = Simulator.get_configs("simulator_preferences_file")
        preferences_df = pd.read_csv(preferences_file)

        fig = px.bar(
            preferences_df,
            x="Scenarios",
            y="Preference",
            title="Preferred Scenario",
            color="Scenarios",
            template=self.template,
        )
        fig.update_layout(font=dict(family=font_family, size=font_size))
        fig.show()

        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=preferences_df["Scenarios"],
                y=preferences_df["Preference"],
                name="Preference",
            )
        )
        fig.update_layout(
            title="Preferred Scenario",
            xaxis_title="Scenarios",
            yaxis_title="Preference",
            template=self.template,
        )
        fig.update_layout(font=dict(family=font_family, size=font_size))
        fig.show()

        if save_fig:
            self.save_plotly(fig, "preferences")

    def plot_mean_speed(self, save_fig=True):
        # Load global font settings from the config file
        font_family = Simulator.get_configs("font_family")  
        font_size = Simulator.get_configs("font_size")  

        # Getting average speed per scenario
        averaged_df = (
            self.df.groupby(["ScenarioID", "Scenario", "Participant"])
            .mean()
            .reset_index()
        )
        filtered_df = averaged_df[averaged_df["Speed"] > 1]
        fig = px.box(
            filtered_df,
            x="Scenario",
            y="Speed",
            title="Mean distance per scenario",
            color="Scenario",
            template=self.template,
        )
        fig.update_layout(legend=dict(x=0.3, y=1.1),font=dict(family=font_family, size=font_size))  # TODO: Play around with location)
        fig.show()

        if save_fig:
            self.save_plotly(fig, "mean_speed")

    def plot_min_distance(self, save_fig=True):
        # Load global font settings from the config file
        font_family = Simulator.get_configs("font_family")  
        font_size = Simulator.get_configs("font_size")  

        # Getting Minimum distance per scenario
        min_df = self.df.groupby(["ScenarioID", "Participant"]).min().reset_index()
        filtered_df = min_df[10 > min_df["Distance"]]

        # Calculate the mean distance for each scenario
        mean_values = filtered_df.groupby("Scenario")["Distance"].mean()

        # Create the box plot
        fig = px.box(
            filtered_df,
            x="Scenario",
            y="Distance",
            title="Comparison of distance across scenarios (mean displayed)",
            color="Scenario",
            template=self.template,
        )

        # Add mean values as annotations
        for scenario, mean in mean_values.items():
            fig.add_annotation(
                x=scenario,
                y=mean,
                text=f"{mean:.2f}",  # Format to 2 decimal places
                showarrow=False,
                font=dict(size=12, color="black"),
                yshift=10  # Adjust position above the box
            )

        # Remove legend
        fig.update_layout(
            
            title=dict(
                text="Comparison of distance across scenarios (mean displayed)",
                x=0.5,  # Center the title
                xanchor="center",  # Ensure text is centered
                y=0.95,  # Adjust the vertical position slightly
                yanchor="top"  # Anchor the title from the top
            ),
            showlegend=False,font=dict(family=font_family, size=font_size))

        fig.show()

        if save_fig:
            self.save_plotly(fig, "min_distance")

    def plot_overtaking_distance(self, save_fig=True):
        # Bin time into 0.5s intervals
        time_bins_filtered = np.arange(4, self.df["Time"].max(), 0.5)
        self.df["TimeBin"] = pd.cut(
            self.df["Time"], bins=time_bins_filtered, labels=time_bins_filtered[:-1]
        )

        # Compute the average overtaking distance for each time bin within each scenario
        df_binned_filtered = (
            self.df.groupby(["TimeBin", "Scenario"])["Distance"].mean().reset_index()
        )
        df_binned_filtered["TimeBin"] = df_binned_filtered["TimeBin"].astype(
            float
        )  # Convert to numeric

        # -----------------------------
        # Create Line Plot (Overtaking Distance Over Time)
        # -----------------------------
        fig_line = px.line(
            df_binned_filtered,
            x="TimeBin",
            y="Distance",
            color="Scenario",
            title="Average Overtaking Distance Over Time for Different Scenarios",
            labels={
                "TimeBin": "Time (s)",
                "Distance": "Average Overtaking Distance (m)",
                "Scenario": "Scenario",
            },
            template=self.template,
        )
        fig.update_layout(font=dict(family=font_family, size=font_size))

        fig_line.show()

        if save_fig:
            self.save_plotly(fig_line, "overtaking_distance")

    def read_data(self, filter_data=True, clean_data=True):
        """Read data into an attribute.

        Args:
            filter_data (bool, optional): flag for filtering data.

        Returns:
            dataframe: updated dataframe.
        """

        scenario_files = os.listdir(self.files_data)

        for scenario in scenario_files:
            scenario_path = os.path.join(self.files_data, scenario)
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

        # print(self.df)
        # self.df = pd.DataFrame()
        # # load csv
        # print("Reading data")
        # for scenario in self.files_data:
        #     # print(scenario)
        #     for dirpath, dirnames, filenames in os.walk(scenario):
        #         # print(dirpath, dirnames, filenames)
        #         scenario_id = dirpath.split("/")[-1].split("_")[-1]
        #         # print(scenario_id)
        #         for particiapant_id, file in enumerate(filenames):
        #             df_temp = pd.read_csv(os.path.join(dirpath, file))
        #             df_temp["ScenarioID"] = int(scenario_id)
        #             df_temp["Scenario"] = self.scenario_names[int(scenario_id)]
        #             df_temp["Participant"] = particiapant_id
        #             # print(file)
        #             self.df = pd.concat([self.df, df_temp])
        # self.df.columns = self.df.columns.str.strip()
        # print(self.df)

        # print(df.head())
        # print(df.info())

        # s_1_df = df[df["Scenario"] == 1 and df["Participant"] == 0]
        # fig = px.line(s_1_df, x="Time", y="Distance")
        # fig.show()

        # df_test = pd.read_csv(
        #     "/home/chachi/code/geo/cyclist-distance-crowdsourced/dcycl/analysis/Simulator/path/Scenario_1/CarCyclistDistanceData.csv"
        # )
        # print(df_test)
        # ax = sns.boxplot(x="Scenario", y="Distance", data=min_distances)
        # print(df.where(df["Scenario"] == 1))
        # print(df_scenario1.groupby("participant").min())
        # for dirpath, dirnames, filenames in os.walk(data):
        #     print(dirpath, dirnames, filenames)
        # df = pd.read_csv(self.files_data[0])

    def save_plotly(
        self,
        fig,
        name,
        width=1320,
        height=680,
        save_eps=False,
        save_png=True,
        save_html=True,
    ):
        """
        Helper function to save figure as html file.

        Args:
            fig (plotly figure): figure object.
            name (str): name of html file.
            width (int, optional): width of figures to be saved.
            height (int, optional): height of figures to be saved.
            save_png (bool, optional): save image as PNG file.
            save_html (bool, optional): save image as html file.
        """
        # # build path
        # path = os.path.join(dc.settings.output_dir, self.folder_figures)
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # # build path for final figure
        # path_final = os.path.join(dc.settings.root_dir, self.folder_figures)
        # print(path_final)
        # save as html
        if save_html:
            py.offline.plot(
                fig,
                filename=os.path.join(self.folder_figures, name + ".html"),
                auto_open=False,
            )
        # save as png
        if save_png:
            fig.write_image(
                os.path.join(self.folder_figures, name + ".png"),
                width=width,
                height=height,
            )
            # also save the final figure

    def filter_data(self, df):
        pass

    def plot_combined_figure(self, save_fig=True):
        # ✅ Load global font settings from the config file
        font_family = Simulator.get_configs("font_family")  # Example: "Open Sans, verdana, arial, sans-serif"
        font_size = Simulator.get_configs("font_size")  # Example: 12

        # Load preferences data
        preferences_file = Simulator.get_configs("simulator_preferences_file")
        preferences_df = pd.read_csv(preferences_file)

        # Ensure data is binned before analysis
        bin_size = 0.5
        self.df = self.bin_data(self.df, 'Time', bin_size)

        # Compute the average overtaking distance per time bin per scenario
        df_binned_filtered = (
            self.df.groupby(["TimeBin", "Scenario"], observed=True)["Distance"].mean().reset_index()
        )

        # Convert TimeBin to numeric
        df_binned_filtered["TimeBin"] = df_binned_filtered["TimeBin"].astype(float)

        # Define the fixed order of scenarios
        scenario_order = [
            "Laser Projection",
            "Vertical Signage",
            "Road Markings",
            "Car Projection System",
            "Center Line and Side-Line Markings",  # Control scenario (S5)
            "Unprotected Cycling Path",
            "No Road Markings"
        ]

        # Define scenario mapping to use S1, S2, etc.
        scenario_mapping = {
            "Laser Projection": "S1",
            "Vertical Signage": "S2",
            "Road Markings": "S3",
            "Car Projection System": "S4",
            "Center Line and Side-Line Markings": "S5",  # Control scenario
            "Unprotected Cycling Path": "S6",
            "No Road Markings": "S7"
        }

        # Define control scenario for statistical comparison
        control_scenario = "Center Line and Side-Line Markings"

        # Compute t-tests between control scenario and other scenarios
        ttest_results = []
        control_distances = df_binned_filtered[df_binned_filtered["Scenario"] == control_scenario]["Distance"]

        for scenario in scenario_order:
            if scenario != control_scenario:
                scenario_distances = df_binned_filtered[df_binned_filtered["Scenario"] == scenario]["Distance"]

                # Perform independent t-test
                t_stat, p_value = stats.ttest_ind(control_distances, scenario_distances, equal_var=False, nan_policy='omit')

                # Convert scenario names to S1, S2, etc.
                s_control = scenario_mapping[control_scenario]  # Always "S5"
                s_scenario = scenario_mapping[scenario]

                # Store result for annotation
                ttest_results.append(f"t-test({s_scenario}, {s_control}): p={p_value:.3f}")

        # Custom color mapping
        scenario_colors = {
            "Laser Projection": "#636EFA",
            "Vertical Signage": "#EF553B",
            "Road Markings": "#00CC96",
            "Car Projection System": "#AB63FA",
            "Center Line and Side-Line Markings": "#FFA15A",
            "Unprotected Cycling Path": "#19D3F3",
            "No Road Markings": "#FF6692",
        }

        # ✅ Proper subplot alignment with adjusted row heights
        fig = make_subplots(
            rows=1, cols=2,  
            column_widths=[0.75, 0.25],  # Ensure the left plot is wider
            shared_yaxes=False,
            horizontal_spacing=0.05  
        )

        # ---- Line Chart (Curvature Graph - Left Side) ----
        for scenario in scenario_order:
            if scenario in df_binned_filtered["Scenario"].values:
                scenario_df = df_binned_filtered[df_binned_filtered["Scenario"] == scenario]
                fig.add_trace(
                    go.Scatter(
                        x=scenario_df["TimeBin"], 
                        y=scenario_df["Distance"], 
                        mode='lines',  
                        name=scenario,
                        line=dict(color=scenario_colors[scenario])
                    ),
                    row=1, col=1  
                )

        # ✅ Set Y-axis labels correctly
        fig.update_yaxes(title_text="Overtaking Distance (m)", range=[0, df_binned_filtered["Distance"].max()], row=1, col=1)

        # ---- Bar Chart (Aligned Right) ----
        for scenario in scenario_order:
            if scenario in preferences_df["Scenarios"].values:
                scenario_df = preferences_df[preferences_df["Scenarios"] == scenario]
                fig.add_trace(
                    go.Bar(
                        x=scenario_df["Scenarios"], 
                        y=scenario_df["Preference"], 
                        name=scenario,
                        marker=dict(color=scenario_colors[scenario]),
                        showlegend=False
                    ),
                    row=1, col=2  
                )

        # ✅ Set Y-axis labels correctly for bar chart
        fig.update_yaxes(title_text="Prefered Scenarios", range=[0, preferences_df["Preference"].max()* 1.75], row=1, col=2)

        # ✅ Align x-axes properly
        fig.update_xaxes(matches="x")  

        # ✅ Layout Adjustments
        fig.update_layout(
            template=self.template,
            showlegend=True,
            width=1320,  
            height=680,  
            font=dict(
            family=font_family,  # Load from config
            size=font_size,  # Load from config
            ),

            # Move Main Title to the Top
            title=dict(
                text="Combined Visualization of Scenario Preferences and Overtaking Distances with Statistical Significance",
                x=0.5,
                y=0.98,
                xanchor="center",
                yanchor="top",
            ),

            # Adjust Legend Position (Fixed Top-Right)
            legend=dict(
                x=0.95,  
                y=0.99,  
                xanchor="right",
                yanchor="top",
                font=dict(size=14),
                traceorder="normal"
            ),
        )

        # ✅ Remove X-axis labels from bar chart to reduce clutter
        fig.update_xaxes(showticklabels=False, title_text="", row=1, col=2)

        # ✅ Adjust subplot titles to match alignment
        fig.update_annotations([
            dict(
                x=0.35, y=-0.12,  
                xref="paper", yref="paper",
                text="Overtaking Distance Over Time",
                showarrow=False,
                font=dict(size=16)
            ),
            dict(
                x=0., y=-0.12,  
                xref="paper", yref="paper",
                text="Preferred Scenario (Space)",
                showarrow=False,
                font=dict(size=16)
            )
        ])

        # ✅ Add t-test results as an annotation at the right side of the figure
        fig.add_annotation(
            x=0.6, y=0.1,  # Position towards the right, properly aligned
            xref="paper", yref="paper",
            text="<br>".join(ttest_results),  # Formatting for better readability
            showarrow=False,
            font=dict(size=14),
            align="left"
        )

        fig.show()

        if save_fig:
            self.save_plotly(fig, "combined_figure")




    def bin_data(self, df, time_column, bin_size):
        """Bin the data into specified intervals."""
        time_bins = np.arange(df[time_column].min(), df[time_column].max() + bin_size, bin_size)
        df['TimeBin'] = pd.cut(df[time_column], bins=time_bins, labels=time_bins[:-1])
        return df

    def perform_ttest(self, scenario1, scenario2, bin_size=0.5):
        """Perform a t-test between two scenarios on overtaking distance."""
        self.df = self.bin_data(self.df, 'Time', bin_size)

        significant_tests = []  # Store only significant p-values
        
        for time_bin in self.df["TimeBin"].unique():
            data1 = self.df[(self.df["Scenario"] == scenario1) & (self.df["TimeBin"] == time_bin)]["Distance"]
            data2 = self.df[(self.df["Scenario"] == scenario2) & (self.df["TimeBin"] == time_bin)]["Distance"]

            if len(data1) > 2 and len(data2) > 2:  # Ensure enough data points
                t_stat, p_value = ttest_ind(data1, data2, equal_var=False)
                if p_value < 0.05:  # ✅ Only store significant results
                    significant_tests.append(p_value)

        # ✅ Return the most significant result (smallest p-value)
        if significant_tests:
            return scenario2, min(significant_tests)  

        return None  # ✅ No significant results





if __name__ == "__main__":
    scenarios_path = Simulator.get_configs("files_simulator")
    sim = Simulator(
        scenarios_path,
        False,
        False,
        False,
    )
    sim.read_data(False, False)

    sim.plot_min_distance()

    sim.plot_mean_speed()

    sim.plot_preferences()

    sim.plot_combined_figure()

    sim.plot_overtaking_distance()

    t_stat, p_value = sim.perform_ttest("Laser Projection", "Vertical Signage")
    print(f"T-statistic: {t_stat}, P-value: {p_value}")
