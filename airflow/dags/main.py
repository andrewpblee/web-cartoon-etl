from dilbert import Dilbert
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from datetime import date

fp = '/Users/Andrew/Documents/data_engineering/database/comics.db'


def update_dilbert(date, db_filepath):
    '''
    Initiates the scrapping of the Dilbert website, then 
    cleans the collected data and transforms it into a dataframe. 
    This dataframe is then added to the dilbert table in the comics database.

    :param date: date of the comic, used as the query param.
    :param db_filepath: Filepath to database
    '''

    d = Dilbert(date)
    scrapped = d.scrape()
    cleaned = d.clean(scrapped)
    loaded = d.load(cleaned)

    # If the database does not exist, create and connect to it.
    engine = create_engine(f'sqlite:///{db_filepath}', echo=False)
    if not database_exists(engine.url):
        create_database(engine.url)

    with engine.connect() as connection:

        print(connection)

        dilbert_table = '''
        CREATE TABLE IF NOT EXISTS dilbert (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            src BLOB NOT NULL,
            alt TEXT NOT NULL,
            tags TEXT NOT NULL,
            transcript BLOB
        )
        '''
        try:
            connection.execute(dilbert_table)
            loaded.to_sql('dilbert', con=engine,
                          if_exists='append', index=False)
        except Exception as e:
            print(e)

        print(f'{date} appended')
