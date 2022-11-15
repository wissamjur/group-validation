import pandas as pd
import numpy as np


def get_genres_as_columns(df, genres):
    for i in genres:
        df[i] = 0
    return df


def get_all_genres_list(df):
    genres = df.genres.to_list()
    user_genre_list = []

    for genre in genres:
        if genre == '(no genres listed)':
            continue
        genre_list = genre.split('|')
        user_genre_list.extend(genre_list)

    return list(set(user_genre_list))


def create_new_genre_records(user_df, modified_ratings, genres, movies, rating=0.5, N=1):
    records_to_add = []
    user_movies = user_df.movieId.to_list()
    target_user = list(set(user_df.userId.to_list()))[0]

    # flip positive ratings
    for genre in genres:
        for n in range(0, N):
            # movies that contain "genre" and are not in the user's seen items
            movie_df = movies[(movies.genres.str.contains(genre)) & ~(movies.movieId.isin(user_movies))]
            random_movie_id = movie_df.sample().movieId.to_list()[0]

            # check if the random item has already been rated by the user.
            # If so, no random record will be added to avoid duplicate ratings.
            seen_movie = modified_ratings[
                (modified_ratings['userId'] == target_user) & (modified_ratings['movieId'] == random_movie_id)
            ]
            if len(seen_movie) == 1:
                continue

            # new record to add
            new_record = {
                'userId': target_user,
                'movieId': random_movie_id,
                'rating': rating,
                'timestamp': 1212603770
            }
            records_to_add.append(new_record)

    return records_to_add


def flip_pofile_ratings(ratings_detailed, movies, target_cluster, N, users_thresh):
    # make a copy of the original ratings df
    modified_ratings = ratings_detailed.copy()
    records_to_add = []

    # threshold to consider for "+ve" feedback (rating >= 3 is considered +ve)
    like_threh = 3

    # users' ratings to modify (only take top k users from every target cluster)
    cluster_df = ratings_detailed[ratings_detailed['cluster'] == target_cluster]
    target_cluster_users = list(set(cluster_df.userId.to_list()))
    target_users = target_cluster_users[:users_thresh]

    for target_user in target_users:
        user_df = cluster_df[cluster_df['userId'] == target_user]
        positive_df = user_df[user_df['rating'] >= like_threh]
        negative_df = user_df[user_df['rating'] < like_threh]

        # get the genres of +ve and -ve items
        positive_genres = get_all_genres_list(positive_df)
        negative_genres = get_all_genres_list(negative_df)

        # create new records with opposite ratings for each genre type (+ve and -ve)
        positive_records = create_new_genre_records(user_df, modified_ratings, positive_genres, movies, rating=0.5, N=N)
        negative_records = create_new_genre_records(user_df, modified_ratings, negative_genres, movies, rating=5, N=N)

        records_to_add.extend(positive_records + negative_records)

    new_records_df = pd.DataFrame(records_to_add)
    final_df = pd.concat([modified_ratings, new_records_df], ignore_index=True)

    return final_df[['userId', 'movieId', 'rating', 'timestamp']]


def add_random_ratings(ratings, clusters, target_cluster, N, users_thresh):
    # make a copy of the original ratings df
    modified_ratings = ratings.copy()
    records_to_add = []

    total_movies = len(list(set(ratings.movieId.to_list())))
    max_rating = max(list(set(ratings.rating.to_list())))
    min_rating = min(list(set(ratings.rating.to_list())))
    # users' ratings to modify (only take top k users from every target cluster)
    cluster_df = clusters[clusters['cluster'] == target_cluster]
    target_cluster_users = list(set(cluster_df.userId.to_list()))
    target_users = target_cluster_users[:users_thresh]

    for target_user in target_users:
        for n in range(N):
            random_movie_id = np.random.choice(np.arange(1, total_movies, 1), size=1)[0]
            random_rating = np.random.choice(np.arange(1, max_rating, min_rating), size=1)[0]

            # check if the random item has already been rated by the user.
            # If so, no random record will be added to avoid duplicate ratings.
            seen_movie = ratings[(ratings['userId'] == target_user) & (ratings['movieId'] == random_movie_id)]
            if len(seen_movie) == 1:
                continue

            # new record to add
            new_record = {
                'userId': target_user,
                'movieId': random_movie_id,
                'rating': random_rating,
                'timestamp': 1212603770
            }

            records_to_add.append(new_record)

    new_records_df = pd.DataFrame(records_to_add)
    final_df = pd.concat([modified_ratings, new_records_df], ignore_index=True)

    return final_df
