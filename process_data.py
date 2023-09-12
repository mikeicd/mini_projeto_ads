import logging

import pandas as pd
import numpy as np
from scipy import stats

logging.basicConfig(
    level=logging.DEBUG,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
)


def filter_df(df, **kwargs):
    filtered_df = df.copy()
    for column_name, value in kwargs.items():
        filtered_df = filtered_df[filtered_df[column_name] == value]
    return filtered_df


def process_data(file):
    df = pd.read_csv(file)
    logging.debug(f"\n{df}")
    return df


def calculate_confidence_interval(
    sample_size, sample_mean, sample_std, confidence_level
):
    degrees_of_freedom = sample_size - 1

    # Calculate the t-score for the given confidence level and degrees of freedom
    t_score = stats.t.ppf((1 + confidence_level) / 2, df=degrees_of_freedom)

    # Calculate the margin of error
    margin_of_error = t_score * (sample_std / np.sqrt(sample_size))

    # Calculate the confidence interval
    lower_bound = sample_mean - margin_of_error
    upper_bound = sample_mean + margin_of_error

    print(
        f"Confidence Interval ({confidence_level*100}%): ({lower_bound}, {upper_bound})"
    )
    
def analize_data(df):
    data = []
    for ut in df['trafego'].unique():
        for up in df['proto'].unique():
            for ub in df['ber'].unique():
                for ud in df['delay'].unique():
                    dff = filter_df(df, trafego=ut, proto=up, ber=ub, delay=ud)
                    mean = dff["transfbits"].mean()
                    std = dff["transfbits"].std()
                    
                    logging.debug(f' Mean = {mean}')
                    logging.debug(f' Std = {std}')
                    
    
            
    


if __name__ == "__main__":
    df = process_data("data/cliente.csv")    
    
    # fdf = filter_df(df, proto='reno')
    # logging.debug(f'\n{fdf}')
    # calculate_confidence_interval(size, mean, std, 0.90)
    analize_data(df)
