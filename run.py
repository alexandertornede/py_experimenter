import utils

config = utils.load_config()
connection, table_name = utils.get_mysql_connection_and_table_name(config)
utils.fill_table(connection, table_name, config)
