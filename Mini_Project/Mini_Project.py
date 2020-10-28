import glob
from Space.space import *
import pandas as pd


def data_path_ml_25m(path_file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'ml-25m', path_file_name)


# csv_files = glob.glob(data_path_ml_25m('*.csv'))

# data_file_names = []
# for file in csv_files:
#     print(file)
#     file = file.strip()
#     file_name = file.split('\\')[-1]
#     data_file_names.append(file_name)
#     print(file_name)

# print(data_file_names, '\n')


print('movies')
df_movies = pd.read_csv(data_path_ml_25m('movies.csv'))

df_movies['release date'] = df_movies['title'].str.extract('.*\((\d\d\d\d)\).*', expand=True)

print(df_movies.head())
print(df_movies.info())
print(len(df_movies), '\n')

print('ratings')
df_ratings = pd.read_csv(data_path_ml_25m('ratings.csv'))
df_ratings.dropna(axis=0, inplace=True)
avg_ratings = df_ratings[['movieId','rating']].groupby('movieId', as_index=False).mean()    # movie avg rating all time
count_ratings = df_ratings[['movieId','rating']].groupby('movieId', as_index=False).count() # count movie rated all time
count_ratings.rename(columns={'rating': 'ratings count'}, inplace=True)
df_ratings['timestamp'] = pd.to_datetime(df_ratings['timestamp'], unit='s')
print(df_ratings.head())
print(len(df_ratings), '\n')

my_ratings = pd.merge(avg_ratings, count_ratings, on='movieId', how='left')
my_named_ratings = pd.merge(df_movies, my_ratings, on='movieId', how='left')

# print('tags')
# df_tags = pd.read_csv(data_path_ml_25m('tags.csv'))
# df_tags['timestamp'] = pd.to_datetime(df_tags['timestamp'], unit='s')
# print(df_tags.head())
# print(len(df_tags), '\n')

df_movies_avg_ratings = pd.merge(df_movies, my_ratings, on='movieId', how='inner')

df_merged = pd.merge(df_movies_avg_ratings, df_ratings, on='movieId', how='inner')


#  movieId, title, genres release date, avg_rating, ratings count, userId, rating, timestamp
df_merged.rename(columns={'rating_x': 'avg_rating','rating_y': 'rating'}, inplace=True)

print(df_merged.head(10))
print(len(df_merged), '\n')

print(my_named_ratings[my_named_ratings['ratings count'] > 10000].sort_values(by='rating',ascending=False).head(50))

my_named_ratings_ordered = my_named_ratings.sort_values(by='ratings count',ignore_index=True)

ratings_scored = my_named_ratings.copy()    # movieId, title, genres, release date, rating, ratings count,
#                                             weighted ratings score
ratings_scored['weighted ratings score'] = ratings_scored['rating']*ratings_scored['ratings count']
ratings_scored.sort_values(by='weighted ratings score', ascending=False, ignore_index=True, inplace=True)

ratings_scored_by_count = ratings_scored.sort_values(by='ratings count', ascending=False, ignore_index=True)
print('\n')
print(ratings_scored.head(50))
print('\n')
print(ratings_scored_by_count)

df_merged_review_year = df_merged.copy()

df_merged_review_year['review year'] = df_merged['timestamp'].values.astype('str')


def date_year(date):
    if date:
        return date[:4]
    else:
        return None


df_merged_review_year['review year'] = df_merged_review_year['review year'].apply(date_year)

print(df_merged_review_year.head())


df_reviews_by_year = df_merged_review_year.groupby('review year').count()
df_mean_rating_by_year = df_merged_review_year.groupby('review year').mean()
df_mean_rating_by_year = df_mean_rating_by_year[['avg_rating', 'rating']]

df_reviews_by_year['year'] = df_reviews_by_year.index
df_reviews_by_year['year'] = df_reviews_by_year['year'].astype(int)
print(df_reviews_by_year[['ratings count', 'year']].corr(), '\n')

df_reviews_by_year_drop95 = df_reviews_by_year.drop(index='1995')
print(df_reviews_by_year_drop95[['ratings count', 'year']].corr(), '\n')

fig1 = plt.figure(1, figsize=(16, 6))
ax_1 = fig1.add_axes([.1, .1, .8, .8])
ax_1.set_ylim([0, 1.8e6])
ax_1.set_xlabel('Year')
ax_1.set_ylabel('Reviews Added')
ax_1.set_title('Movies Reviews Added per Year (Exclude 1995)')
ax_1.plot(df_reviews_by_year_drop95['rating'])

fig2 = plt.figure(2, figsize=(16, 6))
ax_2 = fig2.add_axes([.1, .1, .8, .8])
ax_2.set_ylim([0, 1.8e6])
ax_2.set_xlabel('Year')
ax_2.set_ylabel('Reviews Added')
ax_2.set_title('Movies Reviews Added per Year')
ax_2.plot(df_reviews_by_year['rating'])

print(df_mean_rating_by_year)
plt.show()