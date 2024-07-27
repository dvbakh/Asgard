from db import BotDB

DB_from = BotDB('database.db')
DB_to = BotDB('/data/database.db')

row_all = DB_from.get_all_anketi(132149857)
all = []
for i in row_all:
  if not DB_to.user_exists(DB_from.get_user(i[1])):
    DB_to.add_user(DB_from.get_user(i[1]))
    DB_to.add_anketa(DB_from.get_user(i[1]), i[2], i[6], i[3], i[7], i[5], i[4])
    print('new_added')  
  else:
    print('exists')
