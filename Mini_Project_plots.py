import seaborn as sns
sns.set(style="ticks", color_codes=True,)
import pandas as pd
import os
# import numpy as np
# import time
# from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 15)
sns.set_style('whitegrid')  # 'darkgrid'  grid lines with dark background
#                           # 'white' white background
#                           # 'ticks' ticks on side
#                           # 'whitegrid' grid lines with light background


def data_path_ml_25m(file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'ml-25m', file_name)


df_user_means = pd.read_csv(data_path_ml_25m('user_mean_match_10_24_2020_18_59_41.csv'))
print(df_user_means.head())
print(len(df_user_means), '\n')

print(df_user_means.describe(), '\n')

df_user_means.drop('mean_match',axis=1,inplace=True)
df_user_means = df_user_means[df_user_means['ratings count all years'] >= 100]

df_user_means.rename(columns={'match_mean': 'genre match','no_match_mean': 'genre no match'}, inplace=True)

fig1 = plt.figure(1, figsize=(16, 8))
axes1 = fig1.add_axes([.1, .1, .8, .8])
axes1.set_xlim([1, 5])
# sns.histplot(df_user_means[['genre match', 'genre no match']], kde=False, bins=100, color='b', alpha=.75)


df_user_means_stats = df_user_means.describe()
mu_match = np.round(df_user_means_stats.loc['mean']['genre match'], decimals=2)
mu_no_match = np.round(df_user_means_stats.loc['mean']['genre no match'], decimals=2)
std_match = np.round(df_user_means_stats.loc['std']['genre match'], decimals=2)
std_no_match = np.round(df_user_means_stats.loc['std']['genre no match'], decimals=2)
mu_symbol = u'\u03BC'
sigma_symbol = u'\u03C3'

my_bins = 100
sns.histplot(df_user_means['genre no match'], label='genre no match', kde=False, bins=my_bins, color='salmon', alpha=.9)
sns.histplot(df_user_means['genre match'], label='genre match', kde=False, bins=my_bins, color='b', alpha=.7)
axes1.set_xlabel('User Mean Rating Bins')
axes1.set_ylabel('User Count')
axes1.set_title('User Mean Rating Distributions (Genre Match and Genre No Match)')
axes1.legend(labels=[f'genre no match, {mu_symbol}={mu_no_match}, {sigma_symbol}={std_no_match}',
                     f'genre match,      {mu_symbol}={mu_match}, {sigma_symbol}={std_match}'],
             bbox_to_anchor=(.35, 0.75))
plt.show()

