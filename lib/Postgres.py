import psycopg2


class Postgres:
    def __init__(self, host, port, uesr_name, password, database_name):
        self.connection = psycopg2.connect(database=database_name, user=uesr_name,
                                           password=password, host=host, port=port)
        self.cursor = self.connection.cursor()

    def exe_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()  # SQL INSERT
            return self.cursor.fetchall()
        except Exception as e:
            return e
