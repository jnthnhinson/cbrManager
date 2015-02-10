import sqlite3
import os

#SANATISE YOUR DATA!!!
#Add data w/o overwriting
#NOTE TO SELF: no column found errors often mean add \' \'
#enable user to change series name


validColumns = ['type', 'company', 'storyGroup', 'series', 'volume', 'filename']
validCommands = ['quit', 'filter', 'list', 'help', 'count', 'hello']

def listAll(category):
    c.execute('SELECT ' + category + ', company FROM files GROUP BY ' + category)
    for result in c.fetchall():
        print result[0]


def filterBy(category, target):
    #for row in c.execute('SELECT * FROM files WHERE company=' + company):
    #    print row
    c.execute('SELECT * FROM files WHERE ' + category + '=\'' + target + '\'')
    for result in c.fetchall():
        print result
    
def filterSeriesBy(category, target):
    #for row in c.execute('SELECT * FROM files WHERE company=' + company):
    #    print row
    c.execute('SELECT series FROM files WHERE ' + category + '=\'' + target + '\'')
    for result in c.fetchall():
        print result

# def openSeries(series):
#     # WON'T WORK AS DESIRED. MISSING LOGIC TO GET MOST RECENT.
#     c.execute('SELECT launchable FROM files WHERE series=\'' + series + '\'')
#     results = c.fetchall()
#     #if len(results) == 0: print "File not found."
#     #else: os.system("start " + c.fetchall[0])
#     for r in results:
#         print r[0]
#         os.system("open " + r[0])
#         break
        
def count2(category):
    c.execute('SELECT   ' + category + ', COUNT(*) FROM files GROUP BY ' + category)
    for count in c.fetchall():
        print count[0] + ': ' + str(count[1])
        
def count(category, target):
     c.execute('SELECT COUNT(*) FROM files WHERE ' + category + '=\'' + target + '\'')
     print c.fetchone()[0]

def incr(file):
    c.execute('UPDATE files SET ord = ord + 1 WHERE filename=\'' + file + '\'')
        
def orderFound(series):
    c.execute('SELECT COUNT(*) FROM files WHERE series=\'' + series + '\' AND ord>=0')
    return c.fetchone()[0] >= 1
    #c.execute('UPDATE files SET ord = ord + 1')
    #c.execute('UPDATE files SET ord = ord + 2 WHERE ord >= 0')
        
def openSeries(series):
    # WON'T WORK AS DESIRED. MISSING LOGIC TO GET MOST RECENT.
    
    if (orderFound):
        #open next
        c.execute('SELECT current FROM progress WHERE series=\'' + series + '\'')
        current = c.fetchall()
        '''print current
        print current[0]
        print current[0][0]'''
        if current == None:
            print "That's interesting..."
        else:
            print current
            c.execute('SELECT launchable FROM files WHERE series=\'' + series + '\' AND ord=' + str(current[0][0]))
            result = c.fetchone()
            if (result == None):
                print ("You have already read all titles in the series " + series + ".")
            else:
                print result[0]
                os.system("open " + result[0].replace(" ", "\\ ").replace("(", "\(").replace(")", "\)"))
        
                incrProgress(series)
 
    #if len(results) == 0: print "File not found."
    #else: os.system("start " + c.fetchall[0])

def parseOpen():
    series = raw_input("which series?\n")
    c.execute('UPDATE toContinue SET series=\'' + series + '\'')
    openSeries(series)
        
def parseFilter():
    column = raw_input("column?\n")
    if column not in validColumns:
        print column + " is not a valid column."
    else:
        target = raw_input("target?\n")
        print
        filterBy(column, target)
    
def parseList():
    column = raw_input("which list?\n" + "".join(col + ' ' for col in validColumns) + "\n")
    if column not in validColumns:
        print column + " is not a valid column."
    else:
        print
        listAll(column)
        
def printProgress():
    c.execute('SELECT series, current FROM progress')
    for series in c.fetchall():
        print series[0] + ": " + str(series[1])
    
def printHelp():
    print "Use the following commands:\n" + "".join(command + " " for command in validCommands)
    
def printInvalid():
    print "Invalid command. Type \'help\' for list of commands"
    
def incrProgress(series):
    c.execute('UPDATE progress SET current=current + 1 WHERE series=\'' + series + '\'')
    
def decrProgress(series):
    c.execute('UPDATE progress SET current=current - 1 WHERE series=\'' + series + '\'')   
    
def setProgress(series, current):
    c.execute('UPDATE progress SET current=' + str(current) + ' WHERE series=\'' + series + '\'')    
    
def reset(which):
    if which == "all": c.execute('UPDATE progress SET current=0')   
    else: c.execute('UPDATE progress SET current=0 WHERE series=\'' + which + '\'')   
    
def doesExist(series):
    c.execute('SELECT COUNT(*) FROM files WHERE series=\'' + series + '\'')
    return c.fetchone()[0] > 0
    
def continueReading():
    c.execute('SELECT series FROM toContinue')
    #lastRead in very different meaning than the previous one. Rename and refactor!
    lastRead = c.fetchone()[0]
    print lastRead
    if doesExist(lastRead):
        openSeries(lastRead)
    else:
        print "You have yet to start anything. Try open."
           
def parseInput(input):
    if (input == "quit" or input == "q"):
        conn.commit()
        conn.close()
        return False
    elif (input == "filter" or input == "f"):
        parseFilter()
    elif (input == "list" or input == "l"):
        parseList()
    elif (input == "help" or input == "h"):
        printHelp()
    elif (input == "open" or input == "o"):
        parseOpen()
    elif (input == "count" or input == "c"):
        category = raw_input("which column?")
        count(category, raw_input("target?"))
    elif (input == "incr"):
        incr(raw_input("which file?"))
    elif (input == "hello"):
        print "Hiya!"
    elif (input == "c"):
        count2(raw_input("category?"))
    elif (input == "progress" or input == "p"):
        printProgress()
    elif (input == "++"):
        incrProgress(raw_input("series?"))
    elif (input == "--"):
        decrProgress(raw_input("series?"))
    elif (input == "set"):
        setProgress(raw_input("series?"), raw_input("current?"))
    elif (input == "reset"):
        which = raw_input("which series would you like to reset?")
        if raw_input("Are you sure you wish to reset progress for " + which +"? (y/n)") == "y": reset(which)
    elif (input == "continue" or input == "c"):
        continueReading()
    else:
        printInvalid()

    return True

if __name__ == "__main__":
    os.system('clear')
    conn = sqlite3.connect('allFiles.db')
    c = conn.cursor()
    
    
    running = True;
    print "Welcome to cbrManager!"
    while (running):
        print
        input = raw_input()
        print
        
        running = parseInput(input)
        #try: running = parseInput(input)
        #except: print "error"