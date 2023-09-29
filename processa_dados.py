import logging

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
)


def plot_bar(x, mean, margin):
    plt.bar(x, mean, yerr=margin, align="center", alpha=0.5, ecolor="black", capsize=10)


def plot_confidence_interval(x, mean, margin_error, filtro, color="#2187bb", hlw=0.10):
    left = x - hlw
    top = mean - margin_error
    right = x + hlw
    bottom = mean + margin_error
    plt.plot([bottom, top], [x, x], color=color)
    plt.plot([top, top], [left, right], color=color)
    plt.plot([bottom, bottom], [left, right], color=color)
    plt.plot(mean, x, "o", color="#f44336")


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

    t_score = stats.t.ppf((1 + confidence_level) / 2, df=degrees_of_freedom)

    margin_of_error = t_score * (sample_std / np.sqrt(sample_size))

    return margin_of_error


def analize_data(df):
    result_data = []
    columns = ["bps", "transfbits"]
    for col in columns:
        for ud in df["delay"].unique():
            for ut in df["trafego"].unique():
                i = 0
                plt.figure(figsize=(16, 9))
                filters = []
                for up in df["proto"].unique():
                    for ub in df["ber"].unique():
                        dff = filter_df(df, trafego=ut, proto=up, ber=ub, delay=ud)
                        dff = dff.reset_index(drop=True)
                        filtro = f"{up}"
                        filters.append(filtro)
                        mean = dff[col].mean()
                        std = dff[col].std()
                        margin = calculate_confidence_interval(
                            dff[col].size, mean, std, 0.99
                        )

                        # plot_confidence_interval(i + 1, mean, margin, filtro)
                        plot_bar(i + 1, mean, margin)
                        i += 1

                        result_data.append(
                            (filtro, mean / 10000, std / 1000, margin / 1000, col)
                        )

                # plt.yticks(np.arange(1, len(filters) + 1), filters)
                plt.xticks([1, 2], filters)
                plt.title(f"Intervalo de confiança - {col} - {ud/1000}ns - {ut}")
                plt.savefig(f"data/plots/{col}-{ud/1000}-{ut}.png")
                plt.close()

    return pd.DataFrame(
        result_data,
        columns=["filtro", "mean(M)", "std(K)", "margin_e(K)", "col"],
    )


if __name__ == "__main__":
    df = process_data("data/cliente.csv")
    analized_df = analize_data(df)
    logging.info(f"Resultado da análise \n{analized_df}")
