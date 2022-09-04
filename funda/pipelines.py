import psycopg2
import os
from decouple import config


class FundaPipeline(object):
    """
    Process pipeline for scraped items to Postgresql database
    """

    def __init__(self):
        if os.getenv("SAVE_TO_DIGITAL_OCEAN_DB", config("SAVE_TO_DIGITAL_OCEAN_DB")) == 'True':
            self.hostname = os.getenv("DB_DIGITAL_OCEAN_HOST", config("DB_DIGITAL_OCEAN_HOST"))
            self.username = os.getenv("DB_DIGITAL_OCEAN_USERNAME", config("DB_DIGITAL_OCEAN_USERNAME"))
            self.password = os.getenv("DB_DIGITAL_OCEAN_PASSWORD", config("DB_DIGITAL_OCEAN_PASSWORD"))
            self.database = os.getenv("DB_DIGITAL_OCEAN_NAME", config("DB_DIGITAL_OCEAN_NAME"))
            self.port = os.getenv("DB_DIGITAL_OCEAN_PORT", config("DB_DIGITAL_OCEAN_PORT"))
            self.connection = psycopg2.connect(host=self.hostname,
                                               user=self.username,
                                               password=self.password,
                                               dbname=self.database,
                                               port=self.port)
        else:
            self.hostname = os.getenv("DB_HOST", config("DB_HOST"))
            self.username = os.getenv("DB_USERNAME", config("DB_USERNAME"))
            self.password = os.getenv("DB_PASSWORD", config("DB_PASSWORD"))
            self.database = os.getenv("DB_DATABASE", config("DB_DATABASE"))
            self.connection = psycopg2.connect(host=self.hostname,
                                               user=self.username,
                                               password=self.password,
                                               dbname=self.database)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        """
        Closes connection to database
        @param spider:
        @return: None
        """
        self.cur.close()
        self.connection.close()

    def check_if_exists(self, housenumber: int, zipcode: str):
        """
        Checks if item is in database and returns boolean
        @param housenumber:
        @param zipcode:
        @return: bool true or false
        """
        exists_query = """
        SELECT EXISTS (
        SELECT 1
        FROM 
        public.website_projects_scrapypropertymodel
        WHERE housenumber = %s
        AND
        zipcode = %s
        )
        """
        execute_search_query = self.cur.execute(exists_query, (housenumber, zipcode))
        exists_in_db = self.cur.fetchone()
        return exists_in_db

    def process_item(self, item, spider):
        """ First check if scraped property already exists in Database, otherwise add it to database.
        Returns item after processing.
        @param item:
        @param spider:
        @return:
        """
        save_to_db = os.getenv("SAVE_SCRAPED_DATA_TO_DB", config("SAVE_SCRAPED_DATA_TO_DB"))
        check_if_in_database = self.check_if_exists(item['housenumber'], item['postal_code'])
        if not check_if_in_database[0] and save_to_db == 'True':
            self.cur.execute("insert into website_projects_scrapypropertymodel(street, housenumber, zipcode, city, woon_oppervlak, type_of_property, ask_price, housenumber_add, municipality, status, date_sold, perceel_oppervlak)values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (item['street'], item['housenumber'], item['postal_code'], item['city'], item['area'], item['property_type'], item['price'], item['housenumber_add'] if 'housenumber_add' in item else "", "", item['status'], item['year_sold'], item['plot_size'] if 'plot_size' in item else 0))
            self.connection.commit()
            print("\n Saved to database")
        return item
