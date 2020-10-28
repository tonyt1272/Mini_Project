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


unlisted_genres = set({})  # holds genres not included in master genre dictionary used in get_user_genre_count()
# df_rated = pd.DataFrame()  # used in get_fav_genres() and user_mean_match()


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


# def get_single_user_ratings(single_userid):
#     """
#     :param single_userid:  integer value id a single user id
#     :return df_user_ratings_movies_s: a dataframe with all movie ratings for the single_userid
#     """
#     df_user_ratings_movies_s = df_user_ratings_movies_2[df_user_ratings_movies_2['userId'] ==
#                                                         single_userid].reset_index(drop=True)
#
#     return df_user_ratings_movies_s


def get_fav_genres(df_rated):
    """
    :param df_rated: dataFrame single user's movie ratings with genre info
    :return: three genres most rated by that user (set object),
             A dictionary keys=genres, value=number of times the genre appeared in the user's ratings
    """
    # df_user_ratings_movies = get_single_user_ratings(single_userid)
    # print(df_user_ratings_movies.head())
    genre_dict_user = get_user_genre_count(df_rated)
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


def get_intersection(single_userid):
    df_rated = df_user_ratings_movies_2[df_user_ratings_movies_2['userId'] == single_userid].reset_index(drop=True)
    df_rated['genres'] = df_rated['genres'].map(lambda row: set(row))
    fav_genres = get_fav_genres(df_rated)[0]
    df_rated['intersection fav genres'] = df_rated['genres'].map(lambda row: fav_genres.intersection(row))
    df_rated['intersection value'] = df_rated['genres'].map(lambda row: len(fav_genres.intersection(row)))
    return df_rated


def user_mean_match(single_userid):
    """
    :param single_userid: a user id (integer)
    :return: a dictionary {'match_mean': match_mean, 'no_match_mean': no_match_mean} where a match is defined as the
    intersection of most viewed genres with the genre of each movie that is not an empty set.
    no_match is where the intersection is an empty set.
    """
    df_rated = get_intersection(single_userid)
    df_rated_no_match = df_rated[df_rated['intersection value'] < 1]
    df_rated_match = df_rated[df_rated['intersection value'] >= 1]
    match_mean = df_rated_match['rating'].mean()
    no_match_mean = df_rated_no_match['rating'].mean()
    match_dict = {'match': np.round(match_mean, decimals=4), 'no_match': np.round(no_match_mean, decimals=4)}
    return dict(match_dict)


def user_mean_match_table():
    df_users = df_ratings[['userId', 'movieId', 'rating']].groupby('userId').count()[['rating']].reset_index()
    df_users.rename(columns={'rating': 'ratings count all years'}, inplace=True)
    df_users['mean_match'] = df_users['userId'].apply(user_mean_match)
    # df_users['mean_match'] = df_users['userId'].loc[:199].map(user_mean_match)  # !!testing part of data for speed
    return df_users


# ############ MovieId Data #############
df_movies = pd.read_csv(data_path_ml_25m('movies.csv'))
# df_movies['release date'] = df_movies['title'].str.extract('.*\((\d\d\d\d)\).*', expand=True)
# df_movies_unknown_release_date = df_movies[df_movies['release date'].isna()]
df_movies['genres'] = df_movies['genres'].str.split('|')

df_movies.drop('title', axis=1, inplace=True)

print('movies')
print(df_movies.head())
# print(df_movies.info())
print(len(df_movies), '\n')

# ############ Ratings Data #############
df_ratings = pd.read_csv(data_path_ml_25m('ratings.csv'))

df_ratings['timestamp'] = pd.to_datetime(df_ratings['timestamp'], unit='s')
print('ratings')
print(df_ratings.head())
print(len(df_ratings), '\n')

# ################### match vs no match, mean ratings per user #################
df_user_ratings_movies_2 = pd.merge(df_ratings[['userId', 'movieId', 'rating']], df_movies, on='movieId', how='inner')

start = time.time()
df_user_mean_match = user_mean_match_table()
end = time.time()

df_user_mean_match.dropna(inplace=True)

df_user_mean_match['match_mean'] = df_user_mean_match['mean_match'].apply(lambda x: x['match'])
df_user_mean_match['no_match_mean'] = df_user_mean_match['mean_match'].apply(lambda x: x['no_match'])

df_user_mean_match.to_csv(data_path_ml_25m('user_mean_match_3.csv'), index=False)

print('User mean_match table')
print(df_user_mean_match.head(10), '\n')
print(len(df_user_mean_match), '\n')

delta = end-start
print(f'total run time in seconds: {delta}')