

def get_genres_as_columns(df, genres):
    for i in genres:
        df[i] = 0
    return df


def get_all_genres_list(df):
    genres = df.genres.to_list()
    user_genre_list = []

    for genre in genres:
        if(genre == '(no genres listed)'):
            continue
        genre_list = genre.split('|')
        user_genre_list.extend(genre_list)

    return list(set(user_genre_list))
