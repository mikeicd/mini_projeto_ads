import logging

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
)


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
    plt.plot([mean, mean], [0, 11], color='#5555')
    for index, row in df.iterrows():
        x_value = index + 1
        mean_value = row[col]
        plot_confidence_interval(x_value, mean_value, margin_error)
    plt.savefig(f'data/plots/{col}-{filtro}.png')
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


def calculate_confidence_interval(
    sample_size, sample_mean, sample_std, confidence_level
):
    degrees_of_freedom = sample_size - 1

    t_score = stats.t.ppf((1 + confidence_level) / 2, df=degrees_of_freedom)

    margin_of_error = t_score * (sample_std / np.sqrt(sample_size))

    return margin_of_error


def analize_data(df):
    result_data = []
    for ut in df["trafego"].unique():
        for up in df["proto"].unique():
            for ub in df["ber"].unique():
                for ud in df["delay"].unique():
                    dff = filter_df(df, trafego=ut, proto=up, ber=ub, delay=ud)
                    dff = dff.reset_index(drop=True)
                    filtro = f"{ut}{up}b{ub}d{ud}"
                    logging.debug(dff)

                    tmean = dff["transfbits"].mean()
                    tstd = dff["transfbits"].std()
                    tmargin_e = calculate_confidence_interval(
                        dff["transfbits"].size, tmean, tstd, 0.99
                    )

                    plot_c_interval(dff, tmean, tmargin_e, filtro, "transfbits")

                    bmean = dff["bps"].mean()
                    bstd = dff["bps"].std()
                    bmargin_e = calculate_confidence_interval(
                        dff["bps"].size, bmean, bstd, 0.99
                    )
                    
                    plot_c_interval(dff, bmean, bmargin_e, filtro, "bps")

                    result_data.append(
                        (
                            filtro,
                            tmean,
                            tstd,
                            tmargin_e,
                            bmean,
                            bstd,
                            bmargin_e,
                        )
                    )

    return pd.DataFrame(
        result_data,
        columns=["filtro", "tmean", "tstd", "tmargin_e", "bmean", "bstd", "bmargin_e"],
    )


if __name__ == "__main__":
    df = process_data("data/cliente.csv")
    analized_df = analize_data(df)
    logging.info(f"Resultado da análise \n{analized_df}")
