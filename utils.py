import configparser

import mysql.connector


def load_config():
    """
    Load and return configuration file
    :return: Configuration file
    """

    config = configparser.ConfigParser()
    config.read_file(open('config/configuration.cfg'))
    return config


def get_mysql_connection_and_table_name(config):
    """
    Initialize connection to database based on configuration file. If the tables does not exist, a new one will be
    created automatically
    :param config: Configuration file with database and experiment information
    :return: mysql_connector and table name from the config file
    """

    database_config = config['DATABASE']
    host = database_config['host']
    user = database_config['user']
    database = database_config['database']
    password = database_config['password']
    table_name = database_config['table']

    mysql_connection = mysql.connector.connect(
        host=host,
        user=user,
        database=database,
        password=password
    )

    create_table_if_not_exists(mysql_connection, table_name, config['EXPERIMENT'])

    return mysql_connection, table_name


def create_table_if_not_exists(mysql_connection, table_name, experiment_config) -> None:
    """
    Check if tables does exist. If not, a new table will be created.
    :param mysql_connection: mysql_connector to the database
    :param table_name: name of the table from the config
    :param experiment_config: experiment section of the config file
    """
    cursor = mysql_connection.cursor()
    cursor.execute('SHOW TABLES')

    for table in cursor:
        if table[0] == table_name:
            print('table already exists in database')
            return

    query = create_new_table_query(table_name, experiment_config)

    try:
        cursor.execute(query)
        print('table "%s" created' % table_name)
    except mysql.connector.ProgrammingError as err:
        unkown_datatype = str(err.__context__).split("'")[1].split(" ")[0]
        print("Error: '%s' is unknown or not allowed" % unkown_datatype)


def create_new_table_query(table_name: str, experiment_config) -> str:
    """
    Create new table based on config file
    :param table_name: name of the new table
    :param experiment_config: experiment section of the config file
    :return: query string for new table
    """
    query = 'CREATE TABLE ' + table_name + ' ('
    fields = experiment_config['keyfields'].split(',') + experiment_config['resultfields'].split(',')
    clean_fields = [field.replace(' ', '') for field in fields]
    typed_fields = [tuple(field.split(':')) if len(field.split(':')) == 2 else (field, 'VARCHAR(255)') for
                       field in clean_fields]

    for field, datatype in typed_fields:
        query += '%s %s NOT NULL, ' % (field, datatype)

    # remove last ', '
    query = query[:-2] + ')'

    return query
