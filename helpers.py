from operator import itemgetter


# Function that returns the unique genre list based on the history of a user/s
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


# Maximum likelihood equation
def get_user_max_likelihood(user_id, genre, test_df):
    user_data = test_df[test_df['userId'] == user_id]
    genre_data = user_data.loc[user_data['genres'].str.contains(
        genre, case=False)].sort_values(by='rating', ascending=False)

    num = sum(genre_data.rating.to_list())
    den = sum(user_data.rating.to_list())

    return num / den


def get_ideal_rankings(user_id, test_df, k=10):
    test_df_copy = test_df.copy()
    top_k_ideal = []

    for k in range(1, 11):
        weights = []
        user = test_df_copy[test_df_copy['userId'] == user_id]
        user_genre_list = get_user_genre_list(user_id, test_df_copy)

        for genre in user_genre_list:
            genre_data = user.loc[user['genres'].str.contains(
                genre, case=False)].sort_values(by=['rating', 'count_genres'], ascending=False)

            # calculate gamm from the original test_df
            gamma = get_user_max_likelihood(1, genre, test_df)
            top_rating = genre_data.iloc[0].rating

            next_k = abs(top_rating - gamma)
            weights.append((genre, gamma, next_k))

        # get the top aspect for the weights tuple
        top_aspect = max(weights, key=itemgetter(2))[0]

        genre_data = user.loc[user['genres'].str.contains(top_aspect, case=False)].sort_values(
            by=['rating', 'count_genres'], ascending=False)
        top_item = genre_data.iloc[0]

        # append the top item in the top_k_ideal list
        top_k_ideal.append((top_item.userId, top_item.movieId, top_item.rating))

        # pop the item from the dataframe
        test_df_copy = test_df_copy.drop(genre_data.index.values[0])

    return top_k_ideal
