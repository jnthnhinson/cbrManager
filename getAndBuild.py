import fnmatch
import os
import sqlite3


path = '/Users/jnthnhinson/Documents/Comics'
matches = []
for root, dirnames, filenames in os.walk(path):
  for filename in fnmatch.filter(filenames, '*.cbr'):
    matches.append(os.path.join(root, filename))
    
    
    
conn = sqlite3.connect('allFiles.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS files')
c.execute('CREATE TABLE files (type text, company text, storyGroup text, series text, filename text, launchable text, ord int)')
    

pathLength = len(path.split('/'))  

numInSeries = 0
fileCount = 0
prevSeries = ""
for file in matches:
    parts = file.split('/')
    if parts[pathLength + 3] != prevSeries:
        numInSeries = 0
        prevSeries = parts[pathLength + 3]
    c.execute("INSERT INTO files(type, company, storyGroup, series, filename, launchable, ord) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (parts[pathLength], parts[pathLength+1], parts[pathLength+2], parts[pathLength+3], parts[pathLength+4], file, numInSeries))
    fileCount += 1
    numInSeries += 1

print str(fileCount) + " files in database"   



c.execute('DROP TABLE IF EXISTS progress')
c.execute('CREATE TABLE progress (series text, current int)')

count = 0
c.execute('SELECT series FROM files GROUP BY series')
for result in c.fetchall():
    c.execute("INSERT INTO progress(series, current) VALUES (\'%s\', 0)" % (result[0]))
    count += 1

conn.commit()
conn.close()

'''
We could:
    have a conditional during the insert
    or 
    load all values into dictionary, then set values post-rebuild (what if comics get renamed?)
    
    Can we use the filename to give us ord?

'''
