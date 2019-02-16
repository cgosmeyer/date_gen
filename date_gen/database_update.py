"""
This module serves as an interface for updating the various tables of
the  database, either by inserting new records, or updating
existing ones.

Use:

    This module is intended to be imported from scripts.

    ::

    from database_update import update_master_table

Notes:

    Based on M.Bourque's lightcurve_pipeline `update_database.py`
    module.
"""

import datetime
import numpy as np
import os
import pandas as pd

from database_interface import get_session
from database_interface import load_connection
from database_interface import Food
from database_interface import Activities
from database_interface import Food_Attr
from database_interface import Activities_Attr


def update_master_table(Master, master_dict):
    """Insert or update a record in a master table.
    Unless rebuilding databse, only need to populate the master tables 
    once. 

    Parameters
    ----------
    Master : Table object
        The table in which to insert ``master_dict``.
    master_dict : dict
        A dictionary containing the master information. Each key of 
        ``master_dict`` corresponds to a column in a master
        table of the database.
    """

    # Get the id of the record, if it exists
    session = get_session()
    query = session.query(Master.id)\
        .filter(Master.id == master_dict['master_id']).all()
    if query == []:
        id_num = ''
    else:
        id_num = query[0][0]
    session.close()

    # If id doesn't exist then insert.  If id exists, then update
    insert_or_update(Master, master_dict, id_num)


def insert_or_update(table, data, id_num):
    """
    Insert or update the given database table with the given data.
    This function performs the logic of inserting or updating an
    entry into the hstlc database; if an entry with the given
    'id_num' already exists, then the entry is updated, otherwise a
    new entry is inserted.

    Parameters
    ----------
    table : sqlalchemy.ext.declarative.api.DeclarativeMeta
        The table of the database to update
    data : dict
        A dictionary of the information to update.  Each key of the
        dictionary must be a column in the given table
    id_num : string
        The row ID to update.  If ``id_num`` is blank, then a new row
        is inserted instead.
    """

    from database_interface import engine
    from database_interface import get_session

    session = get_session()
    if id_num == '':
        print("Creating entry for table {}.".format(table))
        engine.execute(table.__table__.insert(), data)
    else:
        print("Updating entry for table {}.".format(table))
        session.query(table)\
            .filter(table.id == id_num)\
            .update(data)
        session.commit()
    session.close()

def populate_from_csv(table, csvfile):
    """ Reads csv file and populates table.
    """
    
    # First read CSV 
    df = pd.read_csv(csvfile)

    # Change dataframe to a dictionary.
    d = df.to_dict('list')

    update_master_table(table, d)

    ## Do some typo checking. ie, that season only one of five possibilities



