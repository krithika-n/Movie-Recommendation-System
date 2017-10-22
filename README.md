# CSE515MultimediaWebDatabases

To load the database:
The database for phase 2 can be loaded from phase2db file if postgres is already installed.
The below command does the job:

psql --set ON_ERROR_STOP=on "database name" < phase2db

db_create and db_load:

The two script uploaded have database creation and loading files.
The db_create creates all tables to an existing database in MySQL called mwdb. Create this database through the MySQL cmd prompt before running this script.
The db_load loads all the csv data into the respective tables with the same name. All '-' characters in the csv file's name have been replaced with '_' in the table name. The names of the csv files are as given by Prof Candan. This script uses a relative file path (like '../phase2_dataset/genome-tags.csv') to locate the csv files. Modify this line to wherever your csv files are stored before running this. Also make sure to remove the headers of the csv, such as (TagID, Tag, Name, Year, et cetera) before running the script. Exception for only one case: genome-tags.csv is loaded into a table with name 'genome', not 'genome_tags'.
