#!/usr/bin/env python

"""

Use:

    python> date_gen.py --in {T/F} --s {spring/summer/winter/fall} --n {int}
    
"""

import argparse
import random
import pandas as pd

from database_interface import get_session
from database_interface import load_connection
from database_interface import Food #, Food_Attr
from database_interface import Activities #, Activities_Attr
from database_update import populate_from_csv

session = get_session()

class DateGen(object):
    def __init__(self, inout, season, nactivities=2):
        """
        """
        # Ensure that parameters are of correct type.
        if 't' in inout.lower():
            self.inout = 1.0
        else:
            self.inout = 0.0
        self.season = season.lower().strip()
        self.nactivities = int(nactivities)

        self.update_db()

    def update_db(self):
        """
        Run database population to ensure database up-to-date with 
        latest entries.
        """
        populate_from_csv(Food, 'database/food.csv')
        populate_from_csv(Activities, 'database/activities.csv')

        print("Database up-to-date.")   

    def query_food(self):
        """
        """
        # Open connection to database and query for given season, in/out.
        if self.season == 'any':
            result_food_item = []
            for season in ['spring', 'summer', 'fall', 'winter']:
                query_food_item = session.query(Food.item).filter(Food.inout == self.inout).filter(Food.season == season).all()
                result_food_item += [result[0] for result in query_food_item]
        else:
            print(session.query(Food.inout).all())
            print("self.inout: ", self.inout)
            print("self.season: ", self.season)
            query_food_item = session.query(Food.item).filter(Food.season == 'any').all()  #filter(Food.inout == 1).
            print("query_food_item: ", query_food_item)
            result_food_item = [result[0] for result in query_food_item]
            print("result_food_item: ", result_food_item)

        ## Need an exception if return no results.

        return result_food_item

    def query_activities(self):
        """
        """
        # Open connection to database and query for given season, in/out.
        if self.season == 'any':
            result_activities_action = []
            result_activities_item = []
            for season in ['spring', 'summer', 'fall', 'winter']:
                query_activities_action = session.query(Activities.action).filter(Activities.inout == self.inout).filter(Activities.season == season).all()
                result_activities_action += [result[0] for result in query_activities_action]   

                query_activities_item = session.query(Activities.item).filter(Food.inout == self.inout).filter(Food.season == season).all()
                result_activities_item += [result[0] for result in query_activities_item]
        else:
            query_activities_action = session.query(Activities.action).filter(Activities.inout == self.inout).filter(Activities.season == self.season).all()
            result_activities_action = [result[0] for result in query_activities_action]    

            query_activities_item = session.query(Activities.item).filter(Food.inout == self.inout).filter(Food.season == self.season).all()
            result_activities_item = [result[0] for result in query_activities_item]

        ## Need an exception if return no results.

        return result_activities_action, result_activities_item

    def random_select(self, arr):
        """
        """
        rand_idx = random.randint(0, len(arr))
        rand_selection = arr[rand_idx]
        return rand_selection, rand_idx

    def food_string(self, food_selection):
        """
        """
        if self.inout == 1:
            print("Stay in and cook {}.".format(food_selection))
        else:
            print("Go out for {}.".format(food_selection))      

    def activities_string(self, activities_action_list, activities_item_list):
        """
        """
        print("And do the following activities: ")

        ## Later add attributes

        for n, action, item in zip(range(self.nactivities), activities_action_list, activities_item_list):
            if item != 'None':
                print("{}. {} {}".format(n+1, action, item))
            else:
                print("{}. {}".format(n+1, action))

    def run(self):
        """
        """

        print("querying for in='{}' and season='{}'".format(self.inout, self.season))

        # Query for food.
        result_food_item = self.query_food()
        print("result_food_item: ", result_food_item)

        # Query for activities.
        result_activities_action, result_activities_item = self.query_activities()
        print("result_activities_action, result_activities_item: ", result_activities_action, result_activities_item)

        # Randomly select a food item.
        food_selection = self.random_select(result_food_item)[0]
        print("food_selection: ", food_selection)

        # Randomly select n activities.
        activities_action_list = []
        activities_item_list = []
        for n in range(self.nactivities):

            # Need use same random index for both action and item.
            rand_idx = self.random_select(result_activities_action)[1]

            activities_action_list.append(result_activities_action[rand_idx])
            activities_item_list.append(result_activities_item[rand_idx])

            ## Need avoid duplicates
            ## Need a warning if fewer results than n

        # Print results
        self.food_string(food_selection)
        self.activities_string(activities_action_list, activities_item_list)


def parse_args():
    """ Parses command line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--in', dest='inout',
        action='store', type=str, required=True, default=True,
        help="Stay in? (True/False)")
    parser.add_argument('--s', dest='season',
        action='store', type=str, required=True, default=True,
        help="Season? (Spring/Summer/Fall/Winter/Any)")
    parser.add_argument('--n', dest='nactivities',
        action='store', type=int, required=False, default=1,
        help="Number of activities? (Default of 1)")    

    args = parser.parse_args()
     
    return args


if __name__=='__main__':
    args = parse_args()

    dg = DateGen(inout=args.inout, season=args.season, nactivities=args.nactivities)
    dg.run()

