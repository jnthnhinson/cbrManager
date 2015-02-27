import sqlite3
import os
import traceback

import cbrParser
import getAndBuild2

#SANATISE YOUR DATA!!!
#Add data w/o overwriting
#NOTE TO SELF: no column found errors often mean add \' \'
#enable user to change series name

#only positive progress
#reset all

path = '/Users/jnthnhinson/Documents/Comics'
fields = ['type', 'company', 'storyGroup', 'series', 'volume', 'filename']

class cbrManager:
    
    def __init__(self):
        print "constructing"
        os.system('clear')
        self.conn = sqlite3.connect('allFiles.db')
        self.c = self.conn.cursor()
        self.parser = cbrParser.parser(self)
        self.tableBuilder = getAndBuild2.TableBuilder(self, self.conn, self.c)
        
    def getSeriesList(self):
        self.c.execute('SELECT series FROM files GROUP BY series')
        seriesList = []
        for series in self.c.fetchall():
            seriesList.append(series[0])
        return seriesList

    def listAll(self, category):
        self.c.execute('SELECT ' + category + ', company FROM files GROUP BY ' + category)
        for result in self.c.fetchall():
            print result[0]


    def filterBy(self, category, target):
        self.c.execute('SELECT * FROM files WHERE ' + category + '=\'' + target + '\'')
        for result in self.c.fetchall():
            print result
    
    def filterSeriesBy(self, category, target):
        self.c.execute('SELECT series FROM files WHERE ' + category + '=\'' + target + '\'')
        for result in self.c.fetchall():
            print result
        
    def count2(self, category):
        self.c.execute('SELECT   ' + category + ', COUNT(*) FROM files GROUP BY ' + category)
        for count in self.c.fetchall():
            print count[0] + ': ' + str(count[1])
        
    def count(self, category, target):
         self.c.execute('SELECT COUNT(*) FROM files WHERE ' + category + '=\'' + target + '\'')
         print self.c.fetchone()[0]
      
    def orderFound(self, series):
        self.c.execute('SELECT COUNT(*) FROM files WHERE series=\'' + series + '\' AND ord>=0')
        return self.c.fetchone()[0] >= 1
        
    def openSeries(self, series):
        self.c.execute('SELECT current FROM progress WHERE series=\'' + series + '\'')
        current = self.c.fetchall()

        print current
        self.c.execute('SELECT launchable FROM files WHERE series=\'' + series + '\' AND ord=' + str(current[0][0]))
        result = self.c.fetchone()
        #error when opening absent series?
        if (result == None):
            print ("You have already read all titles in the series " + series + ".")
        else:
            print result[0]
            os.system("open " + result[0].replace(" ", "\\ ").replace("(", "\(").replace(")", "\)"))

            self.incrProgress(series)

    def open(self, series):
        #series = raw_input("which series?\n")
        self.c.execute('UPDATE toContinue SET series=\'' + series + '\'')
        self.continueExists()
        self.openSeries(series)
        
    def printProgress(self):
        self.c.execute('SELECT series, current FROM progress')
        for series in self.c.fetchall():
            print series[0] + ": " + str(series[1])
            
    def printAllowedFormats(self):
        self.c.execute('SELECT * FROM allowedFormats')
        for series in self.c.fetchall():
            print series[0] + ": " + str(series[1])
    
    def printHelp(self):
        print "Use the following commands:\n" + "".join(command + " " for command in cbrParser.validCommands)
    
    def printInvalid(self):
        print "Invalid command. Type \'help\' for list of commands"
    
    def incrProgress(self, series):
        self.c.execute('UPDATE progress SET current=current + 1 WHERE series=\'' + series + '\'')
    
    def decrProgress(self, series):
        self.c.execute('UPDATE progress SET current=current - 1 WHERE series=\'' + series + '\'')   
    
    def setProgress(self, series, current):
        self.c.execute('UPDATE progress SET current=' + str(current) + ' WHERE series=\'' + series + '\'')    
    
    def reset(self, which):
        if which == "all": self.c.execute('UPDATE progress SET current=0')   
        else: self.c.execute('UPDATE progress SET current=0 WHERE series=\'' + which + '\'')   
        
    def rename(self, targetField, curName, newName):
        #add warning when two fields have same name ()
        self.c.execute('SELECT * FROM files WHERE ' + targetField + '=\'' + curName + '\'')
        value = self.c.fetchone()
        targetPath = path
        for i in range(len(fields)):
            field = fields[i]
            if field == targetField: break
            targetPath += '/' + value[i]
        print targetPath
        currentPath = targetPath + '/' + curName
        newPath = targetPath + '/' + newName
        os.rename(currentPath, newPath)
        
        if targetField == 'series':
            self.c.execute('SELECT current FROM progress WHERE series=\'' + curName + '\'')
            progress = self.c.fetchone()[0]
        
        self.tableBuilder.build()
        
        if targetField == 'series':
            self.setProgress(newName, progress)
            
        #what about continue?
    
    def doesExist(self, series):
        self.c.execute('SELECT COUNT(*) FROM files WHERE series=\'' + series + '\'')
        return self.c.fetchone()[0] > 0
    
    def continueReading(self):
        self.c.execute('SELECT series FROM toContinue')
        #lastRead in very different meaning than the previous one. Rename and refactor!
        temp = self.c.fetchone()
        if temp != None:
            lastRead = temp[0]
            print lastRead
            if self.doesExist(lastRead):
                self.openSeries(lastRead)
            else:
                print "You have yet to start anything. Try open."
        else:
            print "Error. toContinue appears to be missing"
            print "try rebuild"
           
    def allow(self, series, format):
        self.c.execute('INSERT INTO allowedFormats(series, format) VALUES (\'' + series + '\', \'' + format + '\')')
        self.tableBuilder.build()
            
    def disallow(self, series, format):
        self.c.execute('DELETE FROM allowedFormats WHERE series=\'' + series + '\' AND format=\'' + format + '\'')
        self.tableBuilder.build()
           
    def quit(self):
        self.running = False
        
    def build(self):
        self.tableBuilder.build()
    
    def run(self):
        self.running = True;
        print "Welcome to cbrManager!"
    
        while (self.running):
            print
            input = raw_input()
            print
        
            try: self.parser.parseInput(input)
            except: print traceback.format_exc()
    
    def shutdown(self):
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    cbrM = cbrManager()
    cbrM.run()
    cbrM.shutdown()