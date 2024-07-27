import sqlite3

class BotDB:

# name of your database file here 

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def anketa_exists(self, user_id):
        result = self.cursor.execute("SELECT COUNT (*) FROM `anketi` WHERE `users_id` = ?", (self.get_user_id(user_id),))
        result = result.fetchone()[0]

        if result == 0:
            return False
        elif result == 1:
            return True
        else:
            return None

    def get_user_id(self, user_id):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()
        
    def get_user(self, id):
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `id` = ?", (id,))
        return result.fetchone()[0]

    def add_anketa(self, user_id, name, gender, age, favorits, text, link):
        self.cursor.execute("INSERT INTO `anketi` (`users_id`, `name`, `gender`, `age`, `interest`, `text`, `city`) VALUES\
        (?, ?, ?, ?, ?, ?, ?)", (self.get_user_id(user_id), name, gender, age, favorits, text, link))
        return self.conn.commit()

    def update_text(self, user_id, new_text):
        self.cursor.execute("UPDATE `anketi` SET `text` = ? WHERE `users_id` = ?", (new_text, self.get_user_id(user_id)))
        return self.conn.commit()

    def update_inter(self, user_id, new_inter):
        self.cursor.execute("UPDATE `anketi` SET `interest` = ? WHERE `users_id` = ?", (new_inter, self.get_user_id(user_id)))
        return self.conn.commit()

    def get_anketa(self, user_id):
        result = self.cursor.execute("SELECT * FROM `anketi` WHERE `users_id` = ?", (self.get_user_id(user_id),))
        return result.fetchall()

    def delete_anketa(self, user_id):
        self.cursor.execute("DELETE FROM `anketi` WHERE `users_id` = ?", (self.get_user_id(user_id),))
        return self.conn.commit()

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM `users` WHERE `id` = ?", (self.get_user_id(user_id),))
        return self.conn.commit()

    def get_inter(self, user_id):
        result = self.cursor.execute("SELECT `interest` FROM `anketi` WHERE `users_id` = ?", (self.get_user_id(user_id),))
        return result.fetchall()

    def get_seen(self, user_id):
        result = self.cursor.execute("SELECT `gender` FROM `anketi` WHERE `users_id` = ?", (self.get_user_id(user_id),))
        return result.fetchall()

    def update_seen(self, user_id, new_seen_id):
        if self.get_seen(self.get_user_id(user_id)).split(',')[0] == '0':
            seen_id=new_seen_id
        else:
            seen_id=f'{self.get_seen(self.get_user_id(user_id))}, {new_seen_id})'
            self.cursor.execute("UPDATE `anketi` SET `gender` = ? WHERE `users_id` = ?", (new_seen_id, self.get_user_id(user_id),))
        return self.conn.commit()

    def delete_seen(self, user_id):
        self.cursor.execute("UPDATE `anketi` SET `gender` = 0 WHERE `users_id` = ?", (self.get_user_id(user_id),))
        return self.conn.commit()

    def find_anketi(self, user_id, interest, age): 
        some_res = []
        result = self.cursor.execute("SELECT * FROM `anketi` WHERE `users_id` != ? AND `age` BETWEEN ? AND ?", (self.get_user_id(user_id), int(age) - 5, int(age) + 5,))
        for row in result.fetchall():
            if row[0]:
                for el in row:
                    for i in str(interest).split(', '):
                        if str(i).lower() in str(el).lower():
                            some_res.append(row)
        return some_res
        
    def get_all_anketi(self, user_id): 
        some_res = []
        result = self.cursor.execute("SELECT * FROM `anketi` WHERE `users_id` != ?", (self.get_user_id(user_id),))
        for row in result.fetchall():
            if row[0]:
                some_res.append(row)
        return some_res
        
    def close(self):
        self.connection.close()
