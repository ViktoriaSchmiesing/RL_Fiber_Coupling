import os
import pandas as pd
import numpy as np



files = os.listdir('./return_csv_training_long/') #insert folder path
df_total = pd.DataFrame(data=None, index=None)
for file in files:
    df = pd.read_csv('./return_csv_training_long/'+file)
    goal_power, timestamp = file[:-4].split('_')
    print(goal_power, timestamp)
    df["timestamp"] = timestamp
    if timestamp == "1714375298" or timestamp == "1714326368" or timestamp == "1714286125":
        df["goal_power_alg"] = goal_power + "_TQC_pretrained"
        print(goal_power + "_TQC_pretrained")
    else:
        df["goal_power_alg"] = goal_power+"_TQC"
        print(goal_power+"_TQC")
    df["goal_power_timestamp"] = goal_power+"_"+file[-14:-4]
    df["smoothed_value"] = df["Value"].ewm(alpha=0.01).mean()
    df["std1"] = df["Value"].ewm(alpha=0.01).std()
    df["smoothed_value_squared_plus_std1_squared"] = (df["smoothed_value"].apply(lambda x: x**2)
                                                      + df["std1"].apply(lambda x: x**2))
    df_total = pd.concat([df_total, df], ignore_index=True)
print(df_total)
df_total.to_csv("return_trainings_long.csv")

def std_combined(group):
    mean_means = group["smoothed_value"].mean()
    std = np.sqrt(group["smoothed_value_squared_plus_std1_squared"].sum()/(group["smoothed_value"].size)
                  - mean_means**2)
    return pd.Series({"mean": mean_means, "std": std})

stats_df = df_total.groupby(['Step', 'goal_power_alg']).apply(std_combined).reset_index()

stats_df["y_upper"] = stats_df["mean"]+2*stats_df["std"]
stats_df["y_lower"] = stats_df["mean"]-2*stats_df["std"]

stats_df.to_csv("return_trainings_long_stats.csv")
print(stats_df)