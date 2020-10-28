import seaborn as sns
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

sns.set(style="ticks", color_codes=True)
desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 15)
sns.set_style('whitegrid')  # 'darkgrid'  grid lines with dark background
#                           # 'white' white background
#                           # 'ticks' ticks on side
#                           # 'whitegrid' grid lines with light background


def data_path_ml_25m(file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'ml-25m', file_name)


# df_user_means = pd.read_csv(data_path_ml_25m('user_mean_match_10_24_2020_18_59_41.csv'))
df_user_means = pd.read_csv(data_path_ml_25m('user_mean_match_10_25_2020_21_34_05.csv'))
df_user_means.dropna(inplace=True)
df_user_means.drop('mean_match', axis=1, inplace=True)
df_user_means = df_user_means[df_user_means['ratings count all years'] >= 100]

print(df_user_means.head())
print(len(df_user_means), '\n')
print(df_user_means.describe(), '\n')
df_user_means.rename(columns={'match_mean': 'genre match', 'no_match_mean': 'genre no match'}, inplace=True)

fig1 = plt.figure(1, figsize=(16, 8))
axes1 = fig1.add_axes([.1, .1, .8, .8])
axes1.set_xlim([1, 5])

df_user_means_stats = df_user_means.describe()
mu_match = np.round(df_user_means_stats.loc['mean']['genre match'], decimals=2)
mu_no_match = np.round(df_user_means_stats.loc['mean']['genre no match'], decimals=2)
std_match = np.round(df_user_means_stats.loc['std']['genre match'], decimals=2)
std_no_match = np.round(df_user_means_stats.loc['std']['genre no match'], decimals=2)
mu_symbol = u'\u03BC'
sigma_symbol = u'\u03C3'

bins = 100
sns.histplot(df_user_means['genre no match'], label='genre no match', kde=True, bins=bins, color='salmon', alpha=.9)
sns.histplot(df_user_means['genre match'], label='genre match', kde=True, bins=bins, color='b', alpha=.7)
axes1.set_xlabel('User Mean Rating Bins', fontsize=14)
axes1.set_ylabel('User Count', fontsize=14)
axes1.set_title('User Mean Rating Distribution (Genre Match and Genre No Match)', fontsize=16)
axes1.legend(labels=[f'genre no match, {mu_symbol}={mu_no_match}, {sigma_symbol}={std_no_match}',
                     f'genre match,      {mu_symbol}={mu_match}, {sigma_symbol}={std_match}'],
             bbox_to_anchor=(.35, 0.67))

plt.setp(axes1.get_legend().get_texts(), fontsize='14')  # for legend text
# plt.setp(axes1.get_legend().get_title(), fontsize='32') # for legend title

plt.show()
