# group-validation
Code for research paper: Group Validation in Recommender Systems: Framework for Multi-layer Performance Evaluation

# Environment setup
Code environment can be replicated using Anaconda/Docker. All requirements are in the ./requirements.txt file
`$ conda create --name <env> --file requirements.txt`

# Recommender evaluation process
The experiments are based on several notebooks which can be found in the "notebooks" directory. The order of which the notebooks run (in general):
- shrink_dataset.ipynb (optional)
- clean_dataset.ipynb
- clustering.ipynb
- model_experiment.ipynb
- group_validation_experiment.ipynb

