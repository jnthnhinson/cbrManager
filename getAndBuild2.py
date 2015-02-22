import fnmatch
import os
import sqlite3



path = '/Users/jnthnhinson/Documents/Comics'

def tableExists(tableName):
    c.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'' + tableName + '\'')
    if (c.fetchone() == None): return False
    else: return True
    

def loadProgress():
    progress = {}
    for entry in c.execute('SELECT series, current FROM progress'):
        progress[entry[0]] = entry[1]
    return progress
        
def getPaths():
    #path = '/Users/jnthnhinson/Documents/Comics'
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.cbr'):
            matches.append(os.path.join(root, filename))
    
    return matches
    
def getLastRead():
    lastRead = {}
    if tableExists("progress"):
        progress = loadProgress()
        for series in progress:
            c.execute('SELECT launchable FROM files WHERE series=\'' + series + '\' AND ord=' + str(progress[series]))
            temp = c.fetchall()
            if len(temp) > 0:
                print temp
                lastRead[series] = temp[0][0]
            
        return progress, lastRead
    
    
def buildPrimaryTable():
    c.execute('DROP TABLE IF EXISTS files')
    c.execute('CREATE TABLE files (type text, company text, storyGroup text, series text, filename text, launchable text, ord int)')
    
    matches = getPaths()
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
    
    print str(fileCount) + " files total"
    
def buildProgressTable():
    c.execute('DROP TABLE IF EXISTS progress')
    c.execute('CREATE TABLE progress (series text, current int)')

    count = 0
    c.execute('SELECT series FROM files GROUP BY series')
    for result in c.fetchall():
        c.execute("INSERT INTO progress(series, current) VALUES (\'%s\', 0)" % (result[0]))
        count += 1
    
def getOffsets(progress, lastRead):
    print "FINDING OFFSETS..."
    offsets = {}
    for series in lastRead:
        c.execute('SELECT ord FROM files WHERE series=\'' + series + '\' AND launchable=\'' + str(lastRead[series] + '\''))
        newProg = c.fetchone()
        if newProg != None:
            offsets[series] = newProg[0] - progress[series]
            print series + ': x -- ' + str(newProg[0])
            print series + ': z -- ' + str(progress[series])
            print series + ': y  -- ' + str(offsets[series])
        
    return offsets
    
    
    
def updateProgress(progress, lastRead):
    offsets = getOffsets(progress, lastRead)
    print "UPDATING PROGRESS..."

    for series in offsets:
        print series + ': offset           -- ' + str(offsets[series])
        #print series + ': old progress     -- ' + str(progress[series])
        printProgressOf(series)
        c.execute('UPDATE progress SET current = current + ' + str(offsets[series] + progress[series]) + ' WHERE series = \'' + series + '\'')
        printProgressOf(series)
    
    
def printProgressOf(series):
    c.execute('SELECT current FROM progress WHERE series=\'' + series + '\'')
    print series + ': current progress -- ' + str(c.fetchone()[0])
    
def blargh(reset):
    if reset:
        c.execute('DROP TABLE IF EXISTS toContinue')
        
    if not tableExists("toContinue"):
        c.execute('CREATE TABLE toContinue (series text)')
        c.execute('INSERT INTO toContinue(series) VALUES ("not a series")')
      
       
if __name__ == "__main__":
    
    conn = sqlite3.connect('allFiles.db')
    c = conn.cursor()

    progress, lastRead = getLastRead()
    count = buildPrimaryTable()
    
    print progress
    
    buildProgressTable()
    updateProgress(progress, lastRead)
    
    blargh(True)

    conn.commit()
    conn.close()
    
     
    
    
    