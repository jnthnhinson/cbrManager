'''
USELESS?:
incr
cdsa

NO ARGS:
continue
progress
help

ONE ARG:
list field
count field
reset series
++ series
-- series

TWO ARGS:
filter field value
set series value

ONE OR TWO:
open series
open field value

THREE ARGS:
rename field value value

POSSIBLE:



'''
validCommands = ['continue', 'progress', 'help', 'list', 'count', 'reset', '--', '++', 'filter', 'set', 'open', 'rename']

fields = ['type', 'company', 'storyGroup', 'series', 'volume', 'filename']

singles = ['continue', 'progress', 'help', 'quit', 'rebuild', 'c', 'p', 'h', 'q']
duals1 = ['list', 'count', 'ls']
duals2 = ['reset', '++', '--']
trips1 = ['filter']
trips2 = ['set']
quads = ['rename']
flex = ['open', 'o']

duals = duals1 + duals2
trips = trips1 + trips2

class parser:
    
    def __init__(self, manager):
        self.manager = manager
        self.seriesList = manager.getSeriesList()

    def testNumArgs(self, args, expected1, expected2 = -1):
        n = len(args)
    
        if n == expected1 or n == expected2:
            return True
        elif len(args) < expected1:
            print "too few args"
        else:
            print "too many arguments"
        
        return False
    
    def parseSingle(self, operator):
        if operator == 'continue' or operator == 'c':
            self.manager.continueReading()
        elif operator == 'progress' or operator == 'p':
            self.manager.printProgress()
        elif operator == 'help' or operator == 'h':
            self.manager.printHelp()
        elif operator == 'quit' or operator == 'q':
            self.manager.quit()
        elif operator == 'rebuild':
            self.manager.rebuild()
        else:
            print "error"
        
    def parseDual(self, operator, args):
        if operator in duals1:
            self.parseDual1(operator, args)
        elif operator in duals2:
            self.parseDual2(operator, args)
        else:
            print "error"
        
    def parseDual1(self, operator, args):
        if args[0] not in fields:
            print "error"
        
        elif operator == 'list' or operator == 'ls':
            self.manager.listAll(args[0])
        elif operator == 'count':
            self.manager.count2(args[0])
            #should be made flex:
                #count series xmen
                #count series
        else:
            print "error"
        
    def parseDual2(self, operator, args):
        if args[0] not in self.seriesList:
            print "error"
    
        elif operator == 'reset':
            self.manager.reset(args[0])
            self.manager.printProgress()
        elif operator == '++':
            self.manager.incrProgress(args[0])
            self.manager.printProgress()
        elif operator == '--':
            self.manager.decrProgress(args[0])
            self.manager.printProgress()
        else:
            print "error"
        
    def parseTrip(self, operator, args):
        if operator in trips1:
            self.parseTrip1(operator, args)
        elif operator in trips2:
            self.parseTrip2(operator, args)
        else:
            print "error"
        
    def parseTrip1(self, operator, args):
        if args[0] not in fields:
            print "error"
        
        elif operator == 'filter':
            self.manager.filterBy(args[0], args[1])

    def parseTrip2(self, operator, args):
        if args[0] not in self.seriesList:
            print "error"
        
        elif operator == 'set':
            self.manager.setProgress(args[0], args[1])
            self.manager.printProgress()
        
    def parseQuad(self, opeator, args):
        if operator == 'rename':
            self.manager.rename(args[0], args[1], args[2])
            #haven't even started
        
    def parseFlex(self, operator, args):
        if operator == 'open' or operator == 'o':
            if len(args) == 1:
                self.manager.open(args[0])
            else:
                self.manager.open(args[0], args[1])
                #not yet finished

    def parseInput(self, input):
        words = input.split()
        operator = words[0]
        args = words[1:]
    
        if operator in singles:
            valid = self.testNumArgs(args, 0)
            if valid: self.parseSingle(operator)
            
        elif operator in duals:
            valid = self.testNumArgs(args, 1)
            if valid: self.parseDual(operator, args)
        
        elif operator in trips:
            valid = self.testNumArgs(args, 2)
            if valid: self.parseTrip(operator, args)
        
        elif operator in quads:
            valid = self.testNumArgs(args, 3)
            if valid: self.parseQuad(operator, args)
        
        elif operator in flex:
            valid = self.testNumArgs(args, 1, 2)
            if valid: self.parseFlex(operator, args)
            
        else:
            self.manager.printInvalid()
        




