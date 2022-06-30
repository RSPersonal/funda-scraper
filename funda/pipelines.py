import psycopg2
import os
from decouple import config


class FundaPipeline(object):
    """
    Process pipeline for scraped items to Postgresql database
    """

    def __init__(self):
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

    def process_item(self, item, spider):
        """ First check if scraped property already exists in Database, othwise add it to database.
        Returns item after processing.
        @param item:
        @param spider:
        @return:
        """
        self.cur.execute("SELECT street, zipcode from public.website_projects_scrapypropertymodel WHERE housenumber = %s AND  zipcode = %s", (item['housenumber'], item['postal_code']))
        exists_in_db = self.cur.fetchone()
        save_to_db = os.getenv("SAVE_SCRAPED_DATA_TO_DB", config("SAVE_SCRAPED_DATA_TO_DB"))
        if not exists_in_db and save_to_db:
            self.cur.execute("insert into website_projects_scrapypropertymodel(street, housenumber, zipcode, city, woon_oppervlak, type_of_property, ask_price, housenumber_add, municipality)values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (item['street'], item['housenumber'], item['postal_code'], item['city'], item['area'], item['property_type'], item['price'], "", ""))
            self.connection.commit()
        return item
