import fnmatch
import os
import sqlite3

path = '/Users/jnthnhinson/Documents/Comics'

class TableBuilder:
    
    def __init__(self, connection, cursor):
        self.conn = connection
        self.c = cursor

    def tableExists(self, tableName):
        self.c.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'' + tableName + '\'')
        if (self.c.fetchone() == None): return False
        else: return True
    

    def loadProgress(self):
        progress = {}
        for entry in self.c.execute('SELECT series, current FROM progress'):
            progress[entry[0]] = entry[1]
        return progress
        
    def getPaths(self):
        #path = '/Users/jnthnhinson/Documents/Comics'
        matches = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.cbr'):
                matches.append(os.path.join(root, filename))
    
        return matches
    
    def getLastRead(self):
        lastRead = {}
        if self.tableExists("progress"):
            progress = self.loadProgress()
            for series in progress:
                self.c.execute('SELECT launchable FROM files WHERE series=\'' + series + '\' AND ord=' + str(progress[series]))
                temp = self.c.fetchall()
                if len(temp) > 0:
                    print temp
                    lastRead[series] = temp[0][0]
            
            return progress, lastRead
    
    
    def buildPrimaryTable(self):
        self.c.execute('DROP TABLE IF EXISTS files')
        self.c.execute('CREATE TABLE files (type text, company text, storyGroup text, series text, filename text, launchable text, ord int)')
    
        matches = self.getPaths()
        pathLength = len(path.split('/'))

        numInSeries = 0
        fileCount = 0
        prevSeries = ""
        for file in matches:
            parts = file.split('/')
            if parts[pathLength + 3] != prevSeries:
                numInSeries = 0
                prevSeries = parts[pathLength + 3]
            self.c.execute("INSERT INTO files(type, company, storyGroup, series, filename, launchable, ord) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (parts[pathLength], parts[pathLength+1], parts[pathLength+2], parts[pathLength+3], parts[pathLength+4], file, numInSeries))
            fileCount += 1
            numInSeries += 1
    
        print str(fileCount) + " files total"
    
    def buildProgressTable(self):
        self.c.execute('DROP TABLE IF EXISTS progress')
        self.c.execute('CREATE TABLE progress (series text, current int)')

        count = 0
        self.c.execute('SELECT series FROM files GROUP BY series')
        for result in self.c.fetchall():
            self.c.execute("INSERT INTO progress(series, current) VALUES (\'%s\', 0)" % (result[0]))
            count += 1
    
    def getOffsets(self, progress, lastRead):
        print "FINDING OFFSETS..."
        offsets = {}
        for series in lastRead:
            self.c.execute('SELECT ord FROM files WHERE series=\'' + series + '\' AND launchable=\'' + str(lastRead[series] + '\''))
            newProg = self.c.fetchone()
            if newProg != None:
                offsets[series] = newProg[0] - progress[series]
                print series + ': x -- ' + str(newProg[0])
                print series + ': z -- ' + str(progress[series])
                print series + ': y  -- ' + str(offsets[series])
        
        return offsets
    
    
    
    def updateProgress(self, progress, lastRead):
        offsets = self.getOffsets(progress, lastRead)
        print "UPDATING PROGRESS..."

        for series in offsets:
            print series + ': offset           -- ' + str(offsets[series])
            #print series + ': old progress     -- ' + str(progress[series])
            self.printProgressOf(series)
            self.c.execute('UPDATE progress SET current = current + ' + str(offsets[series] + progress[series]) + ' WHERE series = \'' + series + '\'')
            self.printProgressOf(series)
    
    
    def printProgressOf(self, series):
        self.c.execute('SELECT current FROM progress WHERE series=\'' + series + '\'')
        print series + ': current progress -- ' + str(self.c.fetchone()[0])
    
    def blargh(self, reset):
        if reset:
            self.c.execute('DROP TABLE IF EXISTS toContinue')
        
        if not self.tableExists("toContinue"):
            self.c.execute('CREATE TABLE toContinue (series text)')
            self.c.execute('INSERT INTO toContinue(series) VALUES ("not a series")')
        
    def build(self):
        #could pass these through...
        #but that only works if building from cbrManager.
        #maybe that's okay, even desired?

        progress, lastRead = self.getLastRead()
        count = self.buildPrimaryTable()
    
        print progress
    
        self.buildProgressTable()
        self.updateProgress(progress, lastRead)
    
        self.blargh(True)

        self.conn.commit()
        self.conn.close()
      
       
if __name__ == "__main__":
    conn = sqlite3.connect('allFiles.db')
    c = conn.cursor()
    builder = TableBuilder(conn, c)
    builder.build
    
    
     
    
    
    