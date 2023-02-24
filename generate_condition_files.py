import argparse
import os

import numpy as np
import pandas as pd

## generating condition files for the category learning task

## --dims: latent dimensions from which you want to construct
## decision boundaries. note that index starts from 0 here

## --repeat: how many repeats do you want to do for each latent
## dimension

## example usage: python generate_condition_files.py --dims 1 2 3 --repeat 100

## For each repeat the script does the following:
## -> bin the loadings for the given dimension
## -> sample uniformly from the dims for the given dimension
## -> sample random instances of each category
## -> do a median split for the category assignment
## -> write it all to dataframes and export as json files


parser = argparse.ArgumentParser()
parser.add_argument("--dims", nargs="+", type=int)
parser.add_argument("--repeat", type=int)

args = parser.parse_args()
dims = args.dims
repeat = args.repeat

n_trials = 120
loadings = np.loadtxt("spose_embedding_49d_sorted.txt")
stimulus_ids = pd.read_csv("unique_id.csv")
loadings = pd.concat([stimulus_ids, pd.DataFrame(loadings)], axis=1)


file_counter = 1

for i in range(repeat):
    for dim in dims:

        ## bin categories ##
        n_bounds = 6
        start = 0
        stop = 2.
        bin_mask = np.full((loadings.shape[0],), np.inf)

        assert (
            n_trials % (n_bounds - 1) == 0
        ), "n_bounds must divide total image number with no remainders"

        step_boundaries = np.linspace(start, stop, n_bounds)

        for this_bin in range(len(step_boundaries) - 1):

            bin_mask = np.where(
                (loadings[dim] > step_boundaries[this_bin])
                & (loadings[dim] <= step_boundaries[this_bin + 1]),
                this_bin,
                bin_mask,
            )

        bin_unique = np.unique(bin_mask)[:-1]  # do not want inf
        image_per_bin = int(n_trials / len(bin_unique))
        assert np.all(
            np.unique(bin_mask, return_counts=True)[1][:-1] >= image_per_bin
        ), "bins too small for number of samples wanted"

        ## sample categories ##
        categories = []
        category_loadings = []
        for this_bin in bin_unique:

            this_bin_id = np.where(bin_mask == this_bin)[0]
            sampled_ids = np.random.choice(this_bin_id, image_per_bin, replace=False)
            sampled_stimuli = loadings.loc[loadings.index[sampled_ids], "id"].values
            sampled_loadings = loadings.loc[loadings.index[sampled_ids], dim].values

            categories.extend(sampled_stimuli)
            category_loadings.extend(sampled_loadings)

        ## sample images
        images = []
        for category in categories:

            category_path = os.path.join("stimuli", category)
            candidates = os.listdir(category_path)
            chosen = np.random.choice(candidates)
            chosen_path = os.path.join(category_path, chosen)
            images.append(chosen_path)

        cond_file = pd.DataFrame(
            {
                "stimulus": images,
                "loadings": category_loadings,
            }
        )

        cond_file["true_category"] = (
            cond_file.loadings < cond_file.loadings.median()
        ).replace({True: "Julty", False: "Folty"})
        cond_file["true_keyboard"] = np.where(
            cond_file["true_category"] == "Julty", "j", "f"
        )

        cond_file = cond_file.drop(columns=["loadings"])
        cond_file = cond_file.sample(frac=1)
        cond_file.to_json(
            path_or_buf=f"condition_files/{file_counter}.json",
            orient="records",
            indent=4,
        )
        file_counter += 1
