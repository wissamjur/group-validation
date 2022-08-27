from sklearn.cluster import KMeans


def create_clsuters(k, dataset):
    kmeanModel = KMeans(n_clusters=k)
    kmeanModel.fit(dataset)

    # create an extra column in data for storing the cluster values
    dataset['cluster'] = kmeanModel.labels_
    dataset['cluster'].sample(n=10)

    return dataset[["userId", "movieId", "rating", "timestamp", "cluster"]]
