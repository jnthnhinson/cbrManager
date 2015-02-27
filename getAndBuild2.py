import fnmatch
import os
import sqlite3

path = '/Users/jnthnhinson/Documents/Comics'

class TableBuilder:
    
    def __init__(self, manager, connection, cursor):
        self.manager = manager
        self.conn = connection
        self.c = cursor

    def tableExists(self, tableName):
        self.c.execute('SELECT * FROM sqlite_master WHERE type=\'table\' AND name=\'' + tableName + '\'')
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
            for filename in fnmatch.filter(filenames, '*.cb?'):
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
                    #print temp
                    lastRead[series] = temp[0][0]
            
            return progress, lastRead
    
    
    def buildPrimaryTable(self, isPreliminary):
        print "building primary"
        self.c.execute('DROP TABLE IF EXISTS files')
        self.c.execute('CREATE TABLE files (type text, company text, storyGroup text, series text, filename text, launchable text, ord int)')
    
        matches = self.getPaths()
        pathLength = len(path.split('/'))

        broken = []
        numInSeries = 0
        fileCount = 0
        prevSeries = ""
        for file in matches:
            parts = file.split('/')
            if parts[pathLength + 3] != prevSeries:
                numInSeries = 0
                prevSeries = parts[pathLength + 3]
                
            longFileName, extension = os.path.splitext(file)
            if not isPreliminary:
                if not self.isAllowed(prevSeries, extension[1:]):
                    continue
              
            try:
                self.c.execute("INSERT INTO files(type, company, storyGroup, series, filename, launchable, ord) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (parts[pathLength], parts[pathLength+1], parts[pathLength+2], parts[pathLength+3], parts[pathLength+4], file, numInSeries))
                fileCount += 1
                numInSeries += 1
            except:
                broken.append(file)
        
        if not isPreliminary:
            print str(fileCount) + " files total\n"
            print "below files not added due to unknown error:"
            for f in broken: print f
            print
    
    def isAllowed(self, series, format):
        #perhaps switch to series, format, boolean
        #rather than implicit present=true
        #print series + " " + format
        self.c.execute('SELECT * FROM allowedFormats WHERE series=\'' + series + '\' AND format=\'' + format + '\'')
        ret = True if (self.c.fetchone() != None) else False
        return ret
    
    def buildProgressTable(self):
        print "building progress"
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
                #print series + ': x -- ' + str(newProg[0])
                #print series + ': z -- ' + str(progress[series])
                #print series + ': y  -- ' + str(offsets[series])
        
        return offsets
    
    
    
    def updateProgress(self, progress, lastRead):
        offsets = self.getOffsets(progress, lastRead)
        print "UPDATING PROGRESS..."

        for series in offsets:
            #print series + ': offset           -- ' + str(offsets[series])
            #print series + ': old progress     -- ' + str(progress[series])
            #self.printProgressOf(series)
            self.c.execute('UPDATE progress SET current = current + ' + str(offsets[series] + progress[series]) + ' WHERE series = \'' + series + '\'')
            #self.printProgressOf(series)
    
    
    def printProgressOf(self, series):
        self.c.execute('SELECT current FROM progress WHERE series=\'' + series + '\'')
        print series + ': current progress -- ' + str(self.c.fetchone()[0])
    
    def blargh(self, resetFlag):
        if resetFlag:
            self.c.execute('DROP TABLE IF EXISTS toContinue')
        
        if not self.tableExists("toContinue"):
            self.c.execute('CREATE TABLE toContinue (series text)')
            self.c.execute('INSERT INTO toContinue(series) VALUES ("not a series")')
            
    def buildAllowedFormats(self, resetFlag):
        print "building allowedFormats"
        if resetFlag:
            self.c.execute('DROP TABLE IF EXISTS allowedFormats')
            
        if not self.tableExists("allowedFormats"):
            self.c.execute('CREATE TABLE allowedFormats (series text, format text)')
            for series in self.manager.getSeriesList():
                self.c.execute('INSERT INTO allowedFormats(series, format) VALUES (\'' + series + '\', \'cbr\')')
                self.c.execute('INSERT INTO allowedFormats(series, format) VALUES (\'' + series + '\', \'cbz\')')
        
    def build(self):
        #inconsistent naming of helper build functions
        #lame use of resetFlag. What's the point? How will we use it?

        progress, lastRead = self.getLastRead()

        #if not self.tableExists('files'): self.buildPrimaryTable(True)
        self.buildPrimaryTable(True)
        
        self.buildAllowedFormats(False) #uses seriesList, which is not present if first run
        count = self.buildPrimaryTable(False) #must follow above; repeat if necessary
        self.buildProgressTable() #must follow above
        self.updateProgress(progress, lastRead) #must follow above
        self.blargh(True) #must follow above
 
#
# if __name__ == "__main__":
#     conn = sqlite3.connect('allFiles.db')
#     c = conn.cursor()
#     builder = TableBuilder(conn, c)
#     builder.build()
#     self.conn.commit()
#     self.conn.close()
#
     
    
    
    