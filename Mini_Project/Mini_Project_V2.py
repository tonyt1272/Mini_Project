import seaborn as sns
import pandas as pd
import os
import matplotlib.pyplot as plt

desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',15)
sns.set_style('whitegrid')  #'darkgrid'  grid lines with dark background
                            #'white' white background
                            #'ticks' ticks on side
                            #'whitegrid' grid lines with light background


def data_path_ml_25m(path_file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'ml-25m', path_file_name)


# ############ MovieId Data #############

df_movies = pd.read_csv(data_path_ml_25m('movies.csv'))

df_movies['release date'] = df_movies['title'].str.extract('.*\((\d\d\d\d)\).*', expand=True)

df_movies_unknown_release_date = df_movies[df_movies['release date'].isna()]
print('movies')
print(df_movies.head())
print(df_movies.info())
print(len(df_movies), '\n')

# ############ Ratings Data #############

df_ratings = pd.read_csv(data_path_ml_25m('ratings.csv'))

avg_ratings = df_ratings[['movieId','rating']].groupby('movieId', as_index=False).mean('rating')  # Average rating of
#                                                                                            each movie over all time
avg_ratings.rename(columns={'rating': 'avg_rating all years'}, inplace=True)
count_ratings = df_ratings[['movieId','rating']].groupby('movieId', as_index=False).count()  # Count of ratings for each
#                                                                                            movie over all time
count_ratings.rename(columns={'rating': 'ratings count all years'}, inplace=True)

df_ratings['timestamp'] = pd.to_datetime(df_ratings['timestamp'], unit='s')
print('ratings')
print(df_ratings.head())
print(len(df_ratings), '\n')
#
my_ratings = pd.merge(avg_ratings, count_ratings, on='movieId', how='left')
my_named_ratings = pd.merge(df_movies, my_ratings, on='movieId', how='left')

# ############### Merge Movies to User Ratings #################
df_merged = pd.merge(df_ratings, my_named_ratings,  on='movieId', how='left')
df_merged['review year'] = df_merged['timestamp'].values.astype('str')


# ############### Create 'review year' column for sorting ########
# This was faster than .strf() for some reason
def date_year(date):
    if date:
        return date[:4]
    else:
        return None


df_merged['review year'] = df_merged['review year'].apply(date_year)

print('merged DataFrame, df_merged')
print(df_merged.head(10))
print(len(df_merged), '\n')


# ################ Get 'by year' ratings data #################
df_reviews_by_year = pd.DataFrame()
# Number of reviews each year
df_reviews_by_year['total ratings in year'] = df_merged.groupby('review year').count()['rating']
# average of all ratings for all movies in that year
df_reviews_by_year['average rating in year'] = df_merged.groupby('review year').mean('rating')['rating']


df_reviews_by_year['year'] = df_reviews_by_year.index
df_reviews_by_year['year'] = df_reviews_by_year['year'].astype(int)



print('reviews by year correlation')
print(df_reviews_by_year[['total ratings in year', 'year']].corr(), '\n')

df_reviews_by_year_drop95 = df_reviews_by_year.drop(index='1995')
print('reviews by year correlation drop 1995')
print(df_reviews_by_year_drop95[['total ratings in year', 'year']].corr(), '\n')


# ############ New Users per Year ###################
df_user_by_year = df_merged[['userId', 'movieId', 'rating', 'timestamp', 'review year']]
df_user_by_year['review year'] = df_user_by_year['review year'].astype(int)
df_new_users_by_year = df_user_by_year.groupby('userId').min('timestamp')
df_new_users_by_year = df_new_users_by_year.sort_values('review year')
print('new users by year')
print(df_new_users_by_year.head(10), '\n')

df_new_users_by_year_agg = df_new_users_by_year.groupby('review year').count()['rating']
# df_new_users_by_year_agg_drop95 = df_new_users_by_year_agg.drop(index='1995')
print('New users added aggregated by year')
print(df_new_users_by_year_agg, '\n')

df_by_year_data = pd.DataFrame()

df_by_year_data['Users added'] = df_new_users_by_year_agg
df_by_year_data['Total ratings'] = df_reviews_by_year['total ratings in year'].values
print('Correlation of Users added to Total ratings by year')
print(df_by_year_data.corr(), '\n')

# ############### User by Year data #################
df_user_totals = df_user_by_year.groupby(['userId', 'review year']).count()
df_user_totals = df_user_totals[['rating']]
df_user_totals.rename(columns={'rating': 'total ratings'}, inplace=True)
print('User total number of ratings by UserId and year')
print(df_user_totals.head(10), '\n')

print('Sum of all users, total number of ratings by year')
print(df_reviews_by_year, '\n')

# ##################### Ratings per user by year ###################
df_ratings_by_year = df_merged.groupby(['userId', 'review year']).count()[['rating']]
df_ratings_by_year = df_ratings_by_year.reorder_levels(['review year', 'userId']).sort_values('review year')

print('user ratings by year and user')
print(df_ratings_by_year.head(10), '\n')

# ############### User totals #############
df_user_totals_cum = df_ratings.groupby('userId').count()


# ########### Plotting ##################
fig1 = plt.figure(1, figsize=(16, 6))
ax_1 = fig1.add_axes([.1, .1, .8, .8])
ax_1.set_ylim([0, 1.8e6])
ax_1.set_xlabel('Year')
ax_1.set_ylabel('Reviews Added')
ax_1.set_title('Movies Reviews Added per Year (Exclude 1995)')
ax_1.plot(df_reviews_by_year_drop95['total ratings in year'])

fig2 = plt.figure(2, figsize=(16, 6))
ax_2 = fig2.add_axes([.1, .1, .8, .8])
ax_2.set_ylim([0, 1.8e6])
ax_2.set_xlabel('Year')
ax_2.set_ylabel('Reviews Added')
ax_2.set_title('Movies Reviews Added per Year')
ax_2.plot(df_reviews_by_year['total ratings in year'])

fig3 = plt.figure(3, figsize=(16, 6))
ax_3 = fig3.add_axes([.1, .1, .8, .8])
# ax_3.set_ylim([0, 1.8e6])
ax_3.set_xlabel('Year')
ax_3.set_ylabel('Users Added')
ax_3.set_title('New Users Added per Year')
ax_3.plot(df_new_users_by_year_agg)






plt.show()


