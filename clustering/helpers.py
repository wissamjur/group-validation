import pandas as pd


def transform_df(dataset):
    x = dataset.genres
    a = list()
    for i in x:
        abc = i
        a.append(abc.split('|'))
    a = pd.DataFrame(a)
    b = a[0].unique()

    for i in b:
        dataset[i] = 0

    dataset.head(2)

    # we assign "1" to all the columns which are present in the Genres
    for i in b:
        dataset.loc[dataset['genres'].str.contains(i), i] = 1

    # now there is no use of genre
    # since we have movieId, there is no need for the movie names
    dataset = dataset.drop(['genres', 'title'], axis=1)

    return dataset
