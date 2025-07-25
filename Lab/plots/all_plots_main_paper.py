import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import seaborn as sns
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
sns.set(font_scale=1, rc={'text.usetex': True, "font.family": "serif", "font.sans-serif": "Times"})

df_testing_stats = pd.read_csv("./testing/human_vs_agnes_statistics.csv", index_col=0)
df_testing = pd.read_csv("./testing/stats_comparison.csv", index_col=0)
df0 = pd.read_csv("return_trainings_stats"".csv", index_col=0)
df1 = pd.read_csv("return_trainings_long_stats.csv", index_col=0)

palette = sns.color_palette("colorblind")

palette = dict({"0.85_TQC": palette[0], "0.85_SAC": palette[6], "0.87_TQC": palette[8],
                "0.875_TQC_pretrained": palette[9], "0.89_TQC_pretrained": palette[9],
                "0.9_TQC": palette[2], "0.9_TQC_pretrained": palette[9], "human": palette[7], "0.85_CrossQ": palette[1],
                "0.9_CrossQ": palette[3], "0.9_SAC": palette[4]})

hue_order = ['0.87_TQC', '0.9_TQC_pretrained', '0.875_TQC_pretrained', '0.89_TQC_pretrained', "0.9_TQC", '0.9_CrossQ',
             '0.85_CrossQ', '0.85_SAC', '0.9_SAC', '0.85_TQC']
fig3 = plt.figure(figsize=(10, 10), constrained_layout=True)
gs = fig3.add_gridspec(6, 7)

f3_ax1 = fig3.add_subplot(gs[0:2, 0:3])
f3_ax1.set_xlim(0, 40000)

df0 = df0.groupby('goal_power_alg').filter(lambda x: (not (x['goal_power_alg'] == "0.9_TQC").any()))

f3_ax1 = sns.lineplot(data=df0, x="rounded_step", y="mean_norm", hue="goal_power_alg", hue_order=hue_order,
                      legend=False,
                          palette=palette, ax=f3_ax1)
categories = df0['goal_power_alg'].unique()
for category in categories:
    subset = df0[df0['goal_power_alg'] == category]
    f3_ax1.fill_between(subset['rounded_step'], subset['y_lower_norm'], subset['y_upper_norm'], alpha=0.2,
                         color=palette[category])
f3_ax1.plot(37000, 0.83, marker='*', markersize=10, color=palette["0.85_TQC"])
f3_ax1.plot(35000, 0.75, marker='*', markersize=10, color=palette["0.87_TQC"])
f3_ax1.plot(34000, 0.79, marker='*', markersize=10, color=palette["0.85_SAC"])
f3_ax1.plot(34000, 0.75, marker='*', markersize=10, color=palette["0.85_CrossQ"])
f3_ax1.set_xlabel("training steps (rounded to $500$)")
f3_ax1.set_ylabel("normalized return (smoothed)")
title1 = f3_ax1.set_title(r'\textbf{(a)}', fontsize=13)
title1.set_position(np.array([-0.125, 0.99]))


f3_ax2 = fig3.add_subplot(gs[0:2, 3:6])
f3_ax2.set_xlim(0, 215000)

f3_ax2 = sns.lineplot(data=df1, x="Step", y="mean_norm", hue="goal_power_alg", hue_order=hue_order, legend=False,
                          palette=palette, ax=f3_ax2)
categories = df1['goal_power_alg'].unique()
for category in categories:
    subset = df1[df1['goal_power_alg'] == category]
    f3_ax2.fill_between(subset['Step'], subset['y_lower_norm'], subset['y_upper_norm'], alpha=0.2,
                         color=palette[category])
f3_ax2.plot(169000, 0.54, marker='*', markersize=10, color=palette["0.9_TQC"])
f3_ax2.plot(204000, 0.67, marker='*', markersize=10, color=palette["0.9_TQC_pretrained"])
f3_ax2.plot(113000, 0.65, marker='*', markersize=10, color=palette["0.9_CrossQ"])
f3_ax2.plot(122000, 0.47, marker='*', markersize=10, color=palette["0.9_SAC"])

f3_ax2.set_xlabel("training steps")
f3_ax2.set_ylabel("normalized return (smoothed)")
title2 = f3_ax2.set_title(r'\textbf{(b)}', fontsize=13)
title2.set_position(np.array([-0.13, 0.99]))

f3_axl = fig3.add_subplot(gs[0:4, 6:7])


f3_ax3 = fig3.add_subplot(gs[2:4, 0:3])

#f3_ax3 = sns.lineplot(data=df_testing, x="rounded_time_in_s", y="Power", hue="agent", hue_order=hue_order, legend=False, err_style="band",
#                          palette=palette, ax=f3_ax3)
f3_ax3 = sns.lineplot(x='rounded_time_in_s', y='mean', data=df_testing, hue="agent",  hue_order=hue_order, legend=False,
                          palette=palette, ax=f3_ax3)
categories = df_testing['agent'].unique()
for category in categories:
    subset = df_testing[df_testing['agent'] == category]
    f3_ax3.fill_between(subset['rounded_time_in_s'], subset['y_lower'], subset['y_upper'], alpha=0.2,
                         color=palette[category])
# Set y-axis labels for each subplot
f3_ax3.set_ylabel('power')
f3_ax3.set_xlabel('time [seconds]')
f3_ax3.set_xlim(0, 30)
f3_ax3.set_ylim(0, 1)
title3 = f3_ax3.set_title(r'\textbf{(c)}', fontsize=13)
title3.set_position(np.array([-0.125, 0.99]))

f3_ax4 = fig3.add_subplot(gs[4:6, 0:7])
# Plot boxplot for Value1 on the first subplot
df_stats_agnes = df_testing_stats.groupby('agent').filter(lambda x: (not (x['agent'] == "human").any()))
sns.boxplot(x='agent', y='steps_last_episode', data=df_stats_agnes, whis=[0, 100], ax=f3_ax4, hue="agent",
            palette=palette)
sns.stripplot(data=df_stats_agnes, x="agent", y="steps_last_episode", size=2, color=".4", ax=f3_ax4)
f3_ax4.set_xlabel("")
f3_ax4.set_xticks(["0.85_CrossQ", "0.85_SAC", "0.85_TQC", "0.87_TQC", "0.9_CrossQ", "0.9_SAC", "0.9_TQC", "0.9_TQC_pretrained"])
f3_ax4.set_xticklabels(["$P_{goal}=0.85$\nCrossQ", "$P_{goal}=0.85$,\nSAC", '$P_{goal}=0.85$,\nTQC',
                        "$P_{goal}=0.87$\nTQC", "$P_{goal}=0.9$\nCrossQ",
                        "$P_{goal}=0.9$\nSAC", "$P_{goal}=0.9$\nTQC", "$P_{goal}=0.9$\nTQC\npre-trained"])
f3_ax4.set_ylabel("steps to reach $P_{goal}$ in last episode")
title4 = f3_ax4.set_title(r'\textbf{(e)}', fontsize=13)
title4.set_position(np.array([-0.01, 0.99]))


f3_ax5 = fig3.add_subplot(gs[2:4, 3:6])
# Plot boxplot for Value2 on the second subplot
df_stats_human_agnes_0_9 = df_testing_stats.groupby('agent').filter(lambda x: ((x['agent'] == "human").any() or
                                                           (x['agent'] == "0.9_TQC").any() or
                                                           (x['agent'] == "0.9_SAC").any() or
                                                           (x['agent'] == "0.9_CrossQ").any()
                                                           or (x['agent'] == "0.9_TQC_pretrained").any()))
sns.boxplot(x='agent', y='max_time', data=df_stats_human_agnes_0_9, whis=[0, 100], ax=f3_ax5, hue="agent",
            palette=palette)
sns.stripplot(data=df_stats_human_agnes_0_9, x="agent", y="max_time", size=2, color=".4", ax=f3_ax5)
f3_ax5.set_xlabel("")
#f3_ax5.set_ylim(0, 100)
f3_ax5.set_xticks(["0.9_CrossQ", "0.9_SAC", "0.9_TQC", "0.9_TQC_pretrained", "human"])
f3_ax5.set_xticklabels(["CrossQ", "SAC", "TQC", "TQC,\npre-trained", "human"])
f3_ax5.set_ylabel("time to reach $P=0.9$ [seconds]")
title5 = f3_ax5.set_title(r'\textbf{(d)}', fontsize=13)
title5.set_position(np.array([-0.225, 0.99]))

# Create a common legend
labels = ['$P_{goal}=0.85$,\nTQC', '$P_{goal}=0.85$,\nSAC', '$P_{goal}=0.85$,\nCrossQ', '$P_{goal}=0.87$,\nTQC',
          '$P_{goal}=0.9$,\nTQC',
              '$P_{goal}=0.9$,\nTQC,\npre-trained', 'human', '$P_{goal}=0.9$,\nSAC', '$P_{goal}=0.9$,\nCrossQ']
handles = [Line2D([], [], color=palette["0.85_TQC"]), Line2D([], [], color=palette["0.85_SAC"]),
            Line2D([], [], color=palette["0.85_CrossQ"]),
           Line2D([], [], color=palette["0.87_TQC"]), Line2D([], [], color=palette["0.9_TQC"]),
           Line2D([], [], color=palette["0.9_TQC_pretrained"]),  Line2D([], [], color=palette["human"]),
           Line2D([], [], color=palette["0.9_SAC"]), Line2D([], [], color=palette["0.9_CrossQ"])]

orig_pos = f3_axl.get_position(original=True)
legend = fig3.legend(handles, labels, loc='center left', bbox_to_anchor=(orig_pos.x0+0.05, orig_pos.y0+0.32))
fig3.canvas.draw()
fig3.delaxes(f3_axl)

fig3.figure.savefig("main_plot_exp_results.pdf", format="pdf", bbox_inches="tight")

plt.show()
