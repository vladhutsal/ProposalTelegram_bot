def engineers_table_exists(db_query_func):
    def check_existance(self, *args, **kwargs):
        conn = self.create_connection()
        curr = conn.cursor()
        if not curr.lastrowid:
            self.create_engineers_table()

        return db_query_func(self, *args, **kwargs)
    return check_existance
