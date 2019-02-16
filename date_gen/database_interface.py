"""
Module to interface and connect to the database.  
When run as script on command line, creates initial empty
database.

Use:

    Run this as a script in order to create an initial database with all
    empty tables (see the Main).

    ::

    >>> python database_interface.py   

    But primarily this module is intended to be imported from scripts
    in order for the user to interact with the already-built database. 
    These are the importables objects:

    ::

    from database_interface import get_session
    from database_interface import load_connection
    from database_interface import Food
    from database_interface import Activities
    from database_interface import Food_Attr
    from database_interface import Activities_Attr

References:

    http://zetcode.com/db/sqlalchemy/orm/
    http://pythoncentral.io/introductory-tutorial-python-sqlalchemy/

Notes:

    Functions and documentation heavily emulated from M. Bourque's
    hstlc ``database_interface.py`` and various ``pyql`` functions.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Date
from sqlalchemy import Time
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from config import db_name
from config import path_to_db

__all__ = ['Food', 'Activities', 'Food_Attr', 'Activities_Attr']

def get_session():
    """Return the ``session`` object of the database connection
    In many cases, all that is needed is the ``session`` object to
    interact with the database.  This function can be used just to
    establish a connection and retreive the ``session`` object.
    Returns:
        session : sqlalchemy.orm.session.Session
            Provides a holding zone for all objects loaded or associated
            with the database.
    Notes:
        From M. Bourque's 'database_interface.py'
    """

    session, base, engine = load_connection(db_name)

    return session


def load_connection(db_name, echo=False):
    """Create and return a connection to the database given in the
    connection string.

    Parameters
    ----------
    db_name : string
        Name of the SQL Alchemy database in '<name>.db' format.
    echo : bool
            Show all SQL produced

    Returns
    -------
    session : sesson object
        Provides a holding zone for all objects loaded or 
        associated with the database.
    base : base object
        Provides a base class for declarative class definitions.
    engine : engine object
        Provides a source of database connectivity and behavior.
    """
    #Four slashes for absolute path! Three slashes for relative path.
    engine = create_engine('sqlite:///{}/{}'.format(path_to_db, db_name), echo=echo)
    #engine = create_engine('sqlite:////{}/{}'.format(path_to_db, db_name), echo=echo)
    base = declarative_base(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session, base, engine

session, base, engine = load_connection(db_name)


#-------------------------------------------------------------------------------# 
# Define ORMS for Master, Phot, and File Info tables.
#-------------------------------------------------------------------------------# 

def define_columns(class_attributes_dict, header_name):
    """Dynamically define the class attributes for the ORMs.

    Parameters
    -----------
    class_attributes_dict : dictionary
        Don't worry about it.
    header_name : string
        Rootname of the column definitions text file, located in 
        'table_definitions' subdirectory.

    Returns
    -------
    class_attributes_dict : dictionary
        Don't worry about it.
    """
    with open(os.path.join(os.path.split(__file__)[0], 'table_definitions',
                            header_name + '.txt'), 'r') as f:
        data = f.readlines()
    header_keyword_list = [item.strip().split(', ') for item in data]
    for header_keyword in header_keyword_list:
        if header_keyword[1] == 'Integer':
            class_attributes_dict[header_keyword[0].lower()] = Column(Integer())
        elif header_keyword[1] == 'String':
            class_attributes_dict[header_keyword[0].lower()] = Column(String(100))
        #elif header_keyword[1] == 'Boolean':
        #    class_attributes_dict[header_keyword[0].lower()] = Column(Boolean())
        elif header_keyword[1] == 'Float':
            class_attributes_dict[header_keyword[0].lower()] = Column(Float())
        elif header_keyword[1] == 'Date':
            class_attributes_dict[header_keyword[0].lower()] = Column(Date())
        elif header_keyword[1] == 'Time':
            class_attributes_dict[header_keyword[0].lower()] = Column(Time())
        elif header_keyword[1] == 'DateTime':
            class_attributes_dict[header_keyword[0].lower()] = Column(DateTime)
        else:
            raise ValueError('header keyword type not recognized: {}:{}'.format(
                header_keyword[0], header_keyword[1]))

    return class_attributes_dict

def orm_master_factory(class_name):
    """ Creates master classes.

    Parameters
    ----------
    class_name : string
        Name of the Master table class.
    """
    class_attributes_dict = {}
    class_attributes_dict['id'] = Column(Integer, primary_key=True, index=True)
    class_attributes_dict['__tablename__'] = class_name.lower()
    class_attributes_dict = define_columns(class_attributes_dict, 'master') # class_name

    return type(class_name.upper(), (base,), class_attributes_dict)

def orm_attributes_factory(class_name, master_table, master_name):
    """ Creates attributes classes.

    Parameters
    ----------
    class_name : string
        Name of the Attributes class table.
    master_table : Master table class
        Corresponding Master table class, so can link 'id' column.
    master_name : string
        Name of the corresponding Master table.

    Returns
    -------
        tuple of attributes    
    """

    class_attributes_dict = {}
    class_attributes_dict['id'] = Column(Integer, primary_key=True, index=True)
    class_attributes_dict['__tablename__'] = class_name.lower()
    class_attributes_dict = define_columns(class_attributes_dict, class_name.split('_')[1].lower())

    return type(class_name.upper(), (base,), class_attributes_dict)

#-------------------------------------------------------------------------------# 
# Initialize classes.
#-------------------------------------------------------------------------------# 

Food = orm_master_factory('food')
Activities = orm_master_factory('activities')
#Food_Attr = orm_attributes_factory('food_attr', Food, 'food')
#Activities_Attr = orm_attributes_factory('activities_attr', Activities, 'activities')


#-------------------------------------------------------------------------------# 
# Main to create initial empty database
#-------------------------------------------------------------------------------# 

def create_database(base):
    """
    Creates initial database with all empty tables.

    To check that it was created properly, 
    % sqlite3 date_gen.db
    sqlite> .tables
    (Should see all tables.)
    sqlite> pragma table_info(ngc104_fileinfo);
    (Should see all columns. Check each table that they all contain wanted columns)

    Parameters
    ----------
        base : base object
            Don't worry about it.

    Outputs
    -------
        Initial 'date_gen.db' with empty tables.
    """
    base.metadata.create_all()


#-------------------------------------------------------------------------------# 

if __name__=="__main__":

    create_database(base)