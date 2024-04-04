# created by: @madsenav1
from datasets import load_dataset
import pandas as pd
import openpyxl # used for writing to excel to data checking 

class cocktailData:
    def __init__(self):
        # loading in cocktail dataset from HuggingFace
        self.dataset = load_dataset("brianarbuckle/cocktail_recipes", split="train")
        self.df = pd.DataFrame(self.dataset)
        self.liquor = self.liquor_list()

    # converting the HuggingFace dataset to a pandas dataframe for cleaning and manipulation purposes
    def clean_dataset(self):
        # dropping duplicate recipes here to decrease the number of times the same cocktail appears
        cocktail_df = self.df.drop_duplicates(subset="title", keep="first")
        # add in a line later that removes recipes that have strange characters

        # removing some of the recipes that have spelling errors 
        cocktail_df = cocktail_df[~cocktail_df["title"].str.contains("'ss")]

        # removing the recipes with empty ingredients list
        cocktail_df = cocktail_df[cocktail_df["ingredients"].apply(lambda x: len(x) > 1)]

        # removing the recipes with empty spirit list
        cocktail_df = cocktail_df[cocktail_df["ner"].apply(lambda x: len(x) > 0)]

        # removing the recipes with no title
        cocktail_df = cocktail_df[cocktail_df["title"].apply(lambda x: len(x) > 0)]

        # removing the recipes with no directions
        cocktail_df = cocktail_df[cocktail_df["directions"].apply(lambda x: len(x) > 0)]

        # selecting recipes from the books of interest
        cocktail_df = cocktail_df[cocktail_df["source"].isin(["The Joy of Mixology", "PDT", "The Ultimate Bar Book", "IBA", "The Fine Art of Mixing Drinks"])]

        # further cleaning
        cocktail_df = cocktail_df.drop([347, 359, 537, 576, 718, 741])

        # reset index so the random number generator can pull the proper cocktail
        cocktail_df = cocktail_df.reset_index(drop=True)
        return cocktail_df

    # creating the input values for the spirit input
    def liquor_list(self):
        cocktail_df = self.clean_dataset()
        liquor_list = []
        for i in cocktail_df["ner"]:
            for j in i:
                # appending the liquor to the list if it is not in there already
                if (j.title() not in liquor_list):
                    # print(j)
                    liquor_list.append(j.title())
        return sorted(liquor_list)


# checking output here
cocktail = cocktailData()
# cocktail.clean_dataset()
cocktail.liquor