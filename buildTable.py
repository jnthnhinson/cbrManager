


import sqlite3


conn = sqlite3.connect('allFiles.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS files')
c.execute('CREATE TABLE files (type text, company text, storyGroup text, series text, volume text, filename text)')
                                
f = open('/Users/jnthnhinson/Documents/comics/allFiles.text')

for line in f:
    print line
    parts = line.strip().split(';')
    #c.execute("INSERT INTO files VALUES (type %s, company %s, storyGroup %s, series %s, volume %s, filename %s)" % (parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]))
   # print(("%s, %s, %s, %s, %s, %s)" % (parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])))
    c.execute("INSERT INTO files(type, company, storyGroup, series, volume, filename) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')" % (parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]))

conn.commit()
conn.close()