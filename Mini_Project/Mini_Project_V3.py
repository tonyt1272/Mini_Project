import seaborn as sns
import pandas as pd
import os
import numpy as np
import time
import matplotlib.pyplot as plt

desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 15)
sns.set_style('whitegrid')  # 'darkgrid'  grid lines with dark background
#                           # 'white' white background
#                           # 'ticks' ticks on side
#                           # 'whitegrid' grid lines with light background

genres_dict_init = {'Action': 0,
                    'Adventure': 0,
                    'Animation': 0,
                    'Children': 0,
                    'Comedy': 0,
                    'Crime': 0,
                    'Documentary': 0,
                    'Drama': 0,
                    'Fantasy': 0,
                    'Film-Noir': 0,
                    'Horror': 0,
                    'Musical': 0,
                    'Mystery': 0,
                    'Romance': 0,
                    'Sci-Fi': 0,
                    'Thriller': 0,
                    'War': 0,
                    'Western': 0,
                    'IMAX': 0}


unlisted_genres = set({})  # set to hold genres not included in master genre dictionary
df_rated = pd.DataFrame()   # used in get_fav_genres() and user_mean_match()


def data_path_ml_25m(path_file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'ml-25m', path_file_name)


def date_year(date):
    if date:
        return date[:4]
    else:
        return None


def get_user_genre_count(user_movies):
    """
    :param user_movies: A dataframe of user ratings from a single userId
    :return: A dictionary keys=genres, value=number of times the genre appeared in the user's ratings
    """
    genre_dict_user = genres_dict_init.copy()
    for row in range(len(user_movies)):
        for item in user_movies.loc[row]['genres']:
            try:
                genre_dict_user[item] += 1
            except KeyError:
                unlisted_genres.add(item)
    return genre_dict_user


def get_single_user_ratings(single_userid, df_users):
    # global df_ratings_sorted_count
    """
    :param single_userid: integer value, a userId from the dataset
    :param df_users: df with 'userId' and 'ratings count all years'
    :return: DataFrame containing all movie ratings by the given userId
    """
    user_count = df_users[df_users['userId'] == single_userid]['ratings count all years'].values[0]
    user_range = range(user_count)
    # df_user_ratings = df_ratings[df_ratings['userId'] == single_userid][['userId', 'movieId', 'rating']]
    df_user_ratings = df_ratings.loc[user_range]
    df_user_ratings_movies = pd.merge(df_user_ratings, df_movies, on='movieId', how='inner')
    # my_index = single_userid - 1
    print(df_user_ratings_movies.head())
    try:
        df_ratings.drop(user_range, inplace=True)
        df_ratings.reset_index(drop=True, inplace=True)
    except:
        pass
    return df_user_ratings_movies


def get_fav_genres(single_userid):
    """
    :param single_userid: a user id (integer)
    :return: three genres most rated by that user (set object),
             A dictionary keys=genres, value=number of times the genre appeared in the user's ratings
    """
    # df_user_ratings_movies = get_single_user_ratings(single_userid)
    df_user_ratings_movies = df_rated
    # print(df_user_ratings_movies.head())
    genre_dict_user = get_user_genre_count(df_user_ratings_movies)
    genre_dict_initial = genre_dict_user.copy()
    # print(genre_dict_user)

    fav_genres = []
    while (len(fav_genres) < 3) and (sum(genre_dict_user.values()) > 0):
        max_value = max(genre_dict_user.values())
        max_keys = [k for k, v in genre_dict_user.items() if v == max_value]
        for key in max_keys:
            fav_genres.append(key)
            genre_dict_user.pop(key)
    return set(fav_genres[0:3]), genre_dict_user, genre_dict_initial


def get_intersection(single_userid, df_users):
    global df_rated
    df_rated = get_single_user_ratings(single_userid, df_users)

    def to_set(row):
        # refactor to lambda function later
        return set(row)
    df_rated['genres'] = df_rated['genres'].apply(to_set)
    fav_genres = get_fav_genres(single_userid)[0]

    def genre_intersection(row):
        # refactor to lambda function later
        a = fav_genres.intersection(row)
        return a
    df_rated['intersection fav genres'] = df_rated['genres'].apply(genre_intersection)

    def len_genre_intersection(row):
        # refactor to lambda function later
        a = fav_genres.intersection(row)
        return len(a)
    df_rated['intersection value'] = df_rated['genres'].apply(len_genre_intersection)
    return df_rated


def user_mean_match(single_userid, df_users):
    """
    :param single_userid: a user id (integer)
    :return: a dictionary {'match_mean': match_mean, 'no_match_mean': no_match_mean} where a match is defined as the
    intersection of most viewed genres with the genre of each movie that is not an empty set.
    no_match is where the intersection is an empty set.
    """
    df_rated = get_intersection(single_userid, df_users)
    df_rated_no_match = df_rated[df_rated['intersection value'] < 1]
    df_rated_match = df_rated[df_rated['intersection value'] >= 1]
    match_mean = df_rated_match['rating'].mean()
    no_match_mean = df_rated_no_match['rating'].mean()
    match_dict = {'match': np.round(match_mean, decimals=4), 'no_match': np.round(no_match_mean, decimals=4)}
    return match_dict


def user_mean_match_table():
    df_users = df_ratings[['userId', 'movieId', 'rating']].groupby('userId').count()[['rating']].reset_index()
    df_users.rename(columns={'rating': 'ratings count all years'}, inplace=True)
    # df_users['mean_match'] = df_users['userId'].apply(user_mean_match)
    df_users['mean_match'] = df_users['userId'].loc[:2].apply(user_mean_match, df_users=df_users)  # !! .loc[:100] for testing

    return df_users


# ############ MovieId Data #############
df_movies = pd.read_csv(data_path_ml_25m('movies.csv'))
# df_movies['release date'] = df_movies['title'].str.extract('.*\((\d\d\d\d)\).*', expand=True)
# df_movies_unknown_release_date = df_movies[df_movies['release date'].isna()]
df_movies['genres'] = df_movies['genres'].str.split('|')
df_movies.drop('title', axis=1, inplace=True)

print('movies')
print(df_movies.head())
print(df_movies.info())
print(len(df_movies), '\n')

# ############ Ratings Data #############
df_ratings = pd.read_csv(data_path_ml_25m('ratings.csv'))
# df_ratings_sorted_count = df_ratings.groupby(by='userId').count()['rating']

avg_ratings = df_ratings[['movieId', 'rating']].groupby('movieId', as_index=False).mean('rating')  # Average rating of
#                                                                                             each movie over all time
avg_ratings.rename(columns={'rating': 'avg_rating all years'}, inplace=True)

count_ratings = df_ratings[['movieId', 'rating']].groupby('movieId', as_index=False).count()  # Count ratings for each
#                                                                                               movie over all time
count_ratings.rename(columns={'rating': 'ratings count all years'}, inplace=True)

df_ratings['timestamp'] = pd.to_datetime(df_ratings['timestamp'], unit='s')
print('ratings')
print(df_ratings.head())
print(len(df_ratings), '\n')

# #!!Begin comment block for testing!!
# # ############### Merge Movies to User Ratings #################
# my_ratings = pd.merge(avg_ratings, count_ratings, on='movieId', how='left')
# my_named_ratings = pd.merge(df_movies, my_ratings, on='movieId', how='left')
# df_merged = pd.merge(df_ratings, my_named_ratings,  on='movieId', how='left')
# df_merged['review year'] = df_merged['timestamp'].values.astype('str')
#
# # df_merged = pd.read_csv(data_path_ml_25m('df_merged.csv'))    # reading in completed df_merged from HD is slower than
# #                                                                 building from separate DataFrames in memory
#
#
# # df_merged['review year'] = df_merged['review year'].apply(date_year)
#
# print('merged DataFrame, df_merged')
# print(df_merged.head(10))
# print(len(df_merged), '\n')
# #!!End Comment block for testing!!
# ################### match vs no match, mean ratings per user #################
start = time.time()
df_user_mean_match = user_mean_match_table()
end = time.time()

print('User mean_match table')
print(df_user_mean_match.head(10), '\n')

delta = end-start
print(delta)
print(len(df_ratings))
