import logging
import os

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
)


def plot_confidence_interval2(x, mean, margin_error, color="#2187bb", hlw=0.10):
    left = x - hlw
    top = mean - margin_error
    right = x + hlw
    bottom = mean + margin_error
    plt.plot([bottom, top], [x, x], color=color)
    plt.plot([top, top], [left, right], color=color)
    plt.plot([bottom, bottom], [left, right], color=color)
    plt.plot(mean, x, "o", color="#f44336")


def plot_c_interval(df, mean, margin_error, filtro, col):
    logging.debug(df)

    def plot_confidence_interval(x, mean, margin_error, color="#2187bb", hlw=0.10):
        left = x - hlw
        top = mean - margin_error
        right = x + hlw
        bottom = mean + margin_error
        plt.plot([bottom, top], [x, x], color=color)
        plt.plot([top, top], [left, right], color=color)
        plt.plot([bottom, bottom], [left, right], color=color)
        plt.plot(mean, x, "o", color="#f44336")

    lista = df.index.tolist()
    lista = [item + 1 for item in lista]
    plt.yticks(lista)
    plt.title(f"Confidence Interval {col} - {filtro}")
    plt.plot([mean, mean], [0, 25], color="#5555")
    for index, row in df.iterrows():
        x_value = index + 1
        mean_value = row[col]
        plot_confidence_interval(x_value, mean_value, margin_error)
    plt.savefig(f"plots/{col}-{filtro}.png")
    plt.close()


def filter_df(df, **kwargs):
    filtered_df = df.copy()
    for column_name, value in kwargs.items():
        filtered_df = filtered_df[filtered_df[column_name] == value]
    return filtered_df


def process_data(file):
    df = pd.read_csv(file)
    logging.debug(f"\n{df}")
    return df


def list_files(path):
    file_list = []
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            file_list.append(filename)
    return file_list


def contruct_df_by_files(file_list):
    ordem = ["config", "transfbits", "bps", "rep"]
    dataframes = []
    for file in file_list:
        df = process_data("data/" + file)
        df = df.drop(df.index[-1])
        config = file[:-6]
        rep = file[len(file) - 5 : -4]
        df["config"] = config
        df["rep"] = rep
        df = df[ordem]
        dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True)


def calculate_confidence_interval(sample_size, sample_std, confidence_level):
    degrees_of_freedom = sample_size - 1

    t_score = stats.t.ppf((1 + confidence_level) / 2, df=degrees_of_freedom)

    margin_of_error = t_score * (sample_std / np.sqrt(sample_size))

    return margin_of_error


def analize_data(df):
    result_data = []
    columns = ["transfbits", "bps"]
    for col in columns:
        for uc in df["config"].unique():
            dff1 = filter_df(df, config=uc)
            dff1 = dff1.reset_index(drop=True)
            lista = dff1.index.tolist()
            lista = [item + 1 for item in lista]
            dff1_mean = dff1[col].mean()
            plt.yticks(lista)
            plt.title(f"Confidence Interval - {col} - {uc}")
            plt.plot([dff1_mean, dff1_mean], [0.8, 5.2], color="#5555")
            i = 0
            for ur in df["rep"].unique():
                dff2 = filter_df(df, config=uc, rep=ur)
                dff2 = dff2.reset_index(drop=True)
                dff2_std = dff2[col].std()
                dff2_mean = dff2[col].mean()
                margin_error = calculate_confidence_interval(
                    dff2[col].size, dff2[col].std(), 0.99
                )
                plot_confidence_interval2(lista[i], dff2_mean, margin_error)
                i += 1

            result_data.append(
                (
                    uc,
                    col,
                    dff1[col].mean(),
                    dff1[col].std(),
                )
            )
            plt.savefig(f"plots/{col}-{uc}.png")
            plt.close()

    return pd.DataFrame(result_data, columns=["config", "col", "mean", "std"])


if __name__ == "__main__":
    df = contruct_df_by_files(list_files("./data"))
    analized_df = analize_data(df)
    logging.info(f"Resultado da análise \n{analized_df}")
