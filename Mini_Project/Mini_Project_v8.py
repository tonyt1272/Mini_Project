import seaborn as sns
import pandas as pd
import os
import numpy as np
import time
from datetime import datetime


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

genre_dict_user = genres_dict_init.copy()
unlisted_genres = set({})  # holds genres not included in master genre dictionary used in get_user_genre_count()


def data_path_ml_25m(file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'ml-25m', file_name)


def date_year(date):
    """
    slice just the date from the date_time string
    :param date: string from date time
    :return: string year
    """
    if date:
        return date[:4]
    else:
        return None


def scalar_genre_count(row):
    """
    Counts the number of times a user has rated movies from each genre
    :param row:
    :return: Nothing returned, updates are made to the genre_dict_user dictionary in outer scope.  genre_dict_user is
    reset for the next user once operation with current user is complete
    """
    for item in row:
        try:
            genre_dict_user[item] += 1
        except KeyError:
            unlisted_genres.add(item)


vec_get_user_genre_count = np.vectorize(scalar_genre_count, otypes=[set])


def get_fav_genres(df_rated):
    """
    :param df_rated: dataFrame single user's movie ratings with genre info
    :return: three genres most rated by that user (set object),
             A dictionary keys=genres, value=number of times the genre appeared in the user's ratings
    """
    global genre_dict_user

    vec_get_user_genre_count(df_rated['genres'].values)
    # print(genre_dict_user)
    fav_genres = []
    while (len(fav_genres) < 3) and (sum(genre_dict_user.values()) > 0):  # ok to loop here, the genre dict is not that
        max_value = max(genre_dict_user.values())                         # big.
        max_keys = [k for (k, v) in genre_dict_user.items() if v == max_value]
        for key in max_keys:
            fav_genres.append(key)
            genre_dict_user.pop(key)
    genre_dict_user = genres_dict_init.copy()
    return set(fav_genres[0:3])


def get_intersection(single_userid):
    """
    find the intersection of a rated movie's genres with the current user's most viewed genres (fav_genres)
    :param single_userid:
    :return: datafram with user's ratings and the genre intersection
    """
    df_rated = df_user_ratings_movies[df_user_ratings_movies['userId'] == single_userid].reset_index(drop=True)
    fav_genres = get_fav_genres(df_rated)
    # print(fav_genres)
    df_rated['intersection fav genres'] = df_rated['genres'].map(lambda row: fav_genres.intersection(row))
    df_rated['intersection value'] = df_rated['intersection fav genres'].map(lambda row: len(row))

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

    return dict({'match': np.round(df_rated_match['rating'].mean(), decimals=4),
                'no_match': np.round(df_rated_no_match['rating'].mean(), decimals=4)})


def user_mean_match_table():
    df_users = df_ratings[['userId', 'movieId', 'rating']].groupby('userId').count()[['rating']].reset_index()
    df_users.rename(columns={'rating': 'ratings count all years'}, inplace=True)
    # df_users['mean_match'] = df_users['userId'].apply(user_mean_match)  # !!Full run over entire ml-25m
    df_users['mean_match'] = df_users['userId'].loc[:199].map(user_mean_match)  # testing data userId[1] = loc[0:0]
    return df_users


# def user_genre_check_util(single_userid):
#     """
#     Utility Function for checking s single user's 3 most viewed genres, and finding the intersection of those genres
#     with the genres listed in each movie rated by the user.  This was used as QA for values in final processed data set.
#     :param single_userid: integer userid
#     :return: dataframe
#     """
#     global genre_dict_user
#     df_movies_loc = pd.read_csv(data_path_ml_25m('movies.csv'))
#     # df_movies['release date'] = df_movies['title'].str.extract('.*\((\d\d\d\d)\).*', expand=True)
#     # df_movies_unknown_release_date = df_movies[df_movies['release date'].isna()]
#     df_movies_loc['genres'] = df_movies_loc['genres'].str.split('|')
#     df_movies_loc.drop('title', axis=1, inplace=True)
#     df_ratings_loc = pd.read_csv(data_path_ml_25m('ratings.csv'))
#     df_ratings_loc['timestamp'] = pd.to_datetime(df_ratings_loc['timestamp'], unit='s')  # pandas, convert time column
#     df_user_ratings_movies_loc = pd.merge(df_ratings_loc[['userId', 'movieId', 'rating']],
#                                           df_movies_loc, on='movieId', how='inner')
#     df_user_ratings_movies_loc['genres'] = df_user_ratings_movies_loc['genres'].map(lambda row: set(row))  # list to set
#     df_rated = df_user_ratings_movies_loc[df_user_ratings_movies_loc['userId'] == single_userid].reset_index(drop=True)
#
#     fav_genres = get_fav_genres(df_rated)
#     df_rated['intersection fav genres'] = df_rated['genres'].map(lambda row: fav_genres.intersection(row))
#     df_rated['intersection value'] = df_rated['intersection fav genres'].map(lambda row: len(row))
#
#
#     vec_get_user_genre_count(df_rated['genres'].values)
#     print(genre_dict_user)
#     genre_dict_user = genres_dict_init.copy()
#     print(f'userid = {single_userid}\nmost viewed = {fav_genres}', '\n')
#     print(df_rated.head())
#
#     return df_rated


if __name__ == "__main__":
    # ############ MovieId Data #############
    df_movies = pd.read_csv(data_path_ml_25m('movies.csv'))
    # df_movies['release date'] = df_movies['title'].str.extract('.*\((\d\d\d\d)\).*', expand=True)
    # df_movies_unknown_release_date = df_movies[df_movies['release date'].isna()]
    df_movies['genres'] = df_movies['genres'].str.split('|')
    df_movies.drop('title', axis=1, inplace=True)

    print('movies')
    print(df_movies.head())
    print(len(df_movies), '\n')

    # ############ Ratings Data #############
    df_ratings = pd.read_csv(data_path_ml_25m('ratings.csv'))
    df_ratings['timestamp'] = pd.to_datetime(df_ratings['timestamp'], unit='s')  # pandas method, convert time column
    print('ratings')
    print(df_ratings.head())
    print(len(df_ratings), '\n')

    # ################### match vs no match, mean ratings per user #################
    df_user_ratings_movies = pd.merge(df_ratings[['userId', 'movieId', 'rating']], df_movies, on='movieId', how='inner')
    df_user_ratings_movies['genres'] = df_user_ratings_movies['genres'].map(lambda row: set(row))  # list --> set

    start = time.time()  # start time
    df_user_mean_match = user_mean_match_table()    # takes a few hours for entire ml-25m data set to process
    end = time.time()   # stop time
    delta = end-start

    df_user_mean_match.dropna(inplace=True)

    # ##### Unpacking the dictionary column into separate columns #####
    df_user_mean_match['match_mean'] = df_user_mean_match['mean_match'].apply(lambda x: x['match'])
    df_user_mean_match['no_match_mean'] = df_user_mean_match['mean_match'].apply(lambda x: x['no_match'])

    # ##### Write result to .csv #####
    now = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    df_user_mean_match.to_csv(data_path_ml_25m(f'user_mean_match_{now}.csv'), index=False)

    print('User mean_match table')
    print(df_user_mean_match.head(10), '\n')
    print(len(df_user_mean_match), '\n')

    print(f'total run time in seconds: {delta}')
