import math
import numpy as np
import pandas as pd
from helpers.dataset_helpers import get_genres_as_columns, get_all_genres_list


# transform the genres into columns and apply logic to help calculate the DCG/IDCG
def transform_rankings_hits(rankings_hits, genres):
    rankings_hits_reform = rankings_hits.copy()
    rankings_hits_reform = rankings_hits_reform.replace({np.nan: 'None'})
    rankings_hits_reform = get_genres_as_columns(rankings_hits_reform, genres)

    # assign -1 to all the columns (genres) which are present in the row (item) genres,
    # and there is not actual rating on this item from the user
    for genre in genres:
        rankings_hits_reform.loc[(rankings_hits_reform['genres'].str.contains(
            genre)) & (rankings_hits_reform['rating'] == 'None'), genre] = -1

    # assign row.rating to every genre that exists in the item (row) and there is a rating from the user
    for i, row in rankings_hits_reform.iterrows():
        if row.rating != 'None':
            for genre in row.genres.split('|'):
                rankings_hits_reform.loc[i, genre] = row.rating

    return rankings_hits_reform


def get_inner_function(k, genre_ranked_ratings, alpha, beta):
    array_at_k = genre_ranked_ratings[:(k - 1)]
    tao = array_at_k.count(-1)

    first_term = pow((1 - alpha), tao)
    second_term = pow((1 - beta), sum(i > 0 for i in array_at_k))

    return first_term * second_term


def DCG(x, user_id, user_rated_items, user_rankings_hits, likelihood_dict, genres, alpha, beta):
    prob = []

    for genre in genres:
        # get gamma value from likelihood_dict
        gamma = likelihood_dict[genre][user_id - 1][1]

        genre_ranked_ratings = user_rankings_hits[genre].to_list()
        inner_function = get_inner_function(x['rank'], genre_ranked_ratings, alpha, beta)

        if genre in x.genres and x.movieId in user_rated_items:
            prob.append(1 - (beta * gamma * inner_function))
        elif genre in x.genres and x.movieId not in user_rated_items:
            prob.append(1 - (alpha * gamma * inner_function))
        else:
            # thi will always be zero
            prob.append(1 - (0 * gamma * inner_function))
    # gain
    gain = (1 - np.prod(prob))
    # DCG
    dcg = gain / (1 + math.log2(x['rank']))

    return dcg


def get_user_dcg(user_id, rankings_hits, ratings_df, likelihood_dict, k=5):
    user_rankings_hits = rankings_hits[rankings_hits['userId'] == user_id][:k].copy()
    user_rated_items = ratings_df[ratings_df['userId'] == user_id].movieId.to_list()
    genres = get_all_genres_list(ratings_df)

    # get the DCG for the user
    user_rankings_hits['DCG'] = user_rankings_hits.apply(
        lambda x: DCG(
            x,
            user_id,
            user_rated_items,
            user_rankings_hits,
            likelihood_dict,
            genres,
            alpha=0.005,
            beta=0.5
        ), axis=1
    )

    return user_rankings_hits


def get_dcg(rankings_hits, ratings_df, likelihood_dict, k=5):
    dcg = []
    dcg_df_list = []

    # loop over all users
    users = list(set(ratings_df.userId.to_list()))

    for user in users:
        user_dcg = get_user_dcg(user, rankings_hits, ratings_df, likelihood_dict, k)
        dcg.append(sum(user_dcg.DCG.to_list()))
        dcg_df_list.append(user_dcg)

    dcg = sum(dcg)
    dcg_df = pd.concat(dcg_df_list)

    return dcg, dcg_df
