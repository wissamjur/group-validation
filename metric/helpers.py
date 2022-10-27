import pickle
from operator import itemgetter
from collections import defaultdict


def build_all_likelihood_dict(users, genres, ratings_df):
    dataset_likelihoods = defaultdict(list)

    # build all user likelihoods from all available genres
    for genre in genres:
        for user in users:
            max_liklihood = get_user_max_likelihood(user, genre, genres, ratings_df)
            dataset_likelihoods[genre].append((user, max_liklihood))

    # save the dict
    with open("./output/data.pkl", "wb") as pkl_handle:
        pickle.dump(dataset_likelihoods, pkl_handle)


# function that returns the unique genre list based on the history of a user/s
def get_user_genre_list(user_id, test_df):
    user_data = test_df[test_df['userId'] == user_id]
    user_genres = user_data.genres.to_list()
    user_genre_list = []

    for genre in user_genres:
        if(genre == '(no genres listed)'):
            continue
        genre_list = genre.split('|')
        user_genre_list.extend(genre_list)

    return list(set(user_genre_list))


# maximum likelihood equation
def get_user_max_likelihood(user_id, target_genre, genres, ratings_df):
    den_list = []
    user_data = ratings_df[ratings_df['userId'] == user_id]
    genre_data_num = user_data.loc[user_data['genres'].str.contains(target_genre, case=False)]

    # den: loop over all genres. Items might be considered more than once (they might have several genres)
    for genre in genres:
        genre_data_den = user_data.loc[user_data['genres'].str.contains(genre, case=False)]
        den_list.extend(genre_data_den.rating.values)

    num = sum(genre_data_num.rating.to_list())
    den = sum(den_list)

    return num / den


# function that gets the idea rankings used to calculate the IDCG of alpha-beta-nDCG
def get_ideal_rankings(user_id, likelihood_dict, test_df, k=10):
    test_df_copy = test_df.copy()
    top_k_ideal = []

    # loop over "k"
    for k in range(1, k + 1):
        weights = []
        user = test_df_copy[test_df_copy['userId'] == user_id]
        user_genre_list = get_user_genre_list(user_id, test_df_copy)

        for genre in user_genre_list:
            genre_data = user.loc[user['genres'].str.contains(
                genre, case=False)].sort_values(by=['rating', 'count_genres'], ascending=False)

            # calculate gamma from the original test_df (pre-calculated, load from dict)
            gamma = likelihood_dict[genre][user_id - 1][1]

            top_rating = genre_data.iloc[0].rating

            next_k = abs(top_rating - gamma)
            weights.append((genre, gamma, next_k))

        # get the top aspect for the weights tuple
        top_aspect = max(weights, key=itemgetter(2))[0]

        genre_data = user.loc[user['genres'].str.contains(top_aspect, case=False)].sort_values(
            by=['rating', 'count_genres'], ascending=False)
        top_item = genre_data.iloc[0]

        # append the top item in the top_k_ideal list
        top_k_ideal.append((top_item.userId, top_item.movieId, top_item.rating, k))

        # pop the item from the dataframe
        test_df_copy = test_df_copy.drop(genre_data.index.values[0])

    return top_k_ideal
