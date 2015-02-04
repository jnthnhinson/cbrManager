import sqlite3
import os

#SANATISE YOUR DATA!!!
#Add data w/o overwriting
#NOTE TO SELF: no column found errors often mean add \' \'

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
        c.execute('SELECT launchable FROM files WHERE series=\'' + series + '\' AND ord=' + str(current[0][0]))
        result = c.fetchone()
        if (result == None):
            print ("You have already read all titles in the series " + series + ".")
        else:
            print result[0]
            os.system("open " + result[0])
        
            incrProgress(series)
 
    #if len(results) == 0: print "File not found."
    #else: os.system("start " + c.fetchall[0])

def parseOpen():
    series = raw_input("which series?\n")
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
           
def parseInput(input):
    if (input == "quit"):
        conn.commit()
        conn.close()
        return False
    elif (input == "filter"):
        parseFilter()
    elif (input == "list"):
        parseList()
    elif (input == "help"):
        printHelp()
    elif (input == "open"):
        parseOpen()
    elif (input == "count"):
        category = raw_input("which column?")
        count(category, raw_input("target?"))
    elif (input == "incr"):
        incr(raw_input("which file?"))
    elif (input == "hello"):
        print "Hiya!"
    elif (input == "c"):
        count2(raw_input("category?"))
    elif (input == "progress"):
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