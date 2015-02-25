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
validCommands = ['continue', 'progress', 'help', 'list', 'count', 'reset', '--', '++', 'filter', 'set', 'open', 'rename', 'rebuild']

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

    # def testNumArgs(self, args, expected1, expected2 = -1, errorFunc):
#         n = len(args)
#
#         if n == expected1 or n == expected2:
#             return True
#         elif len(args) < expected1:
#             #print "too few args"
#             errorFunc()
#         else:
#             #print "too many arguments"
#             errorFunc()
#
#         return False
    
    def testNumArgs(self, args, expected1, errorFunc = None):
        n = len(args)
    
        if n == expected1:
            return True
        elif len(args) < expected1:
            #print "too few args"
            if errorFunc != None: errorFunc()
        else:
            #print "too many arguments"
            if errorFunc != None: errorFunc()
        
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
            self.manager.build()
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
            self.duals1Error(operator)
        
        elif operator == 'list' or operator == 'ls':
            self.manager.listAll(args[0])
        elif operator == 'count':
            self.manager.count2(args[0])
            #should be made flex:
                #count series xmen
                #count series
            #current:
                #count series:
                    #Saga: 12
                    #Xmen: 33
            #alt:
                #count series:
                    #2 series found
        else:
            print "error"
        
    def parseDual2(self, operator, args):
        if args[0] not in self.seriesList:
            self.duals2Error(operator)
    
        elif operator == 'reset':
            self.manager.reset(args[0])
            self.manager.printProgress()
        elif operator == '++':
            self.manager.incrProgress(args[0])
            self.manager.printProgress()
        elif operator == '--':
            self.manager.decrProgress(args[0])
            self.manager.printProgress()
        
    def parseTrip(self, operator, args):
        if operator in trips1:
            self.parseTrip1(operator, args)
        elif operator in trips2:
            self.parseTrip2(operator, args)
        
    def parseTrip1(self, operator, args):
        if args[0] not in fields:
            self.trips1Error(operator)
        
        elif operator == 'filter':
            self.manager.filterBy(args[0], args[1])

    def parseTrip2(self, operator, args):
        if args[0] not in self.seriesList:
            self.trips2Error(operator)
        
        elif operator == 'set':
            self.manager.setProgress(args[0], args[1])
            self.manager.printProgress()
        
    def parseQuad(self, operator, args):
        if operator == 'rename':
            self.manager.rename(args[0], args[1], args[2])
            self.seriesList = self.manager.getSeriesList()
        
    def parseOpen(self, operator, args):
        if operator == 'open' or operator == 'o':
            if len(args) == 1 and args[0] in self.seriesList:
                self.manager.open(args[0])
            elif len(args) == 2 and args[0] in fields:
                self.manager.open(args[0], args[1])
                #not yet finished
            else:
                self.openError()
                
    def duals1Error(self, operator):
        print "Error: Syntax error. Use following format:"
        print operator + " fieldName"
        
    def duals2Error(self, operator):
        print "Error: Syntax error. Use following format:"
        print operator + " seriesName"
        
    def trips1Error(self, operator):
        print "Error: Syntax error. Use following format:"
        print operator + " fieldName"
        
    def trips2Error(self, operator):
        print "Error: Syntax error. Use following format:"
        print operator + " seriesName"
        
    def quadsError(self, operator):
        print "Error: Syntax error. Use following format:"
        print operator + " fieldName curName, newName"
        
    def openError(self):
        print "Error: Syntax error. Use following format:"
        print "open seriesName"
        print "open fieldName fieldValue"

    def parseInput(self, input):
        words = input.split()
        operator = words[0]
        args = words[1:]
    
        if operator in singles:
            valid = self.testNumArgs(args, 0)
            if valid: self.parseSingle(operator)
            
        elif operator in duals1:
            valid = self.testNumArgs(args, 1, lambda: self.duals1Error(operator))
            if valid: self.parseDual(operator, args)
            
        elif operator in duals2:
            valid = self.testNumArgs(args, 1, lambda: self.duals2Error(operator))
            if valid: self.parseDual(operator, args)
        
        elif operator in trips1:
            valid = self.testNumArgs(args, 2, lambda: self.trips1Error(operator))
            if valid: self.parseTrip(operator, args)
            
        elif operator in trips2:
            valid = self.testNumArgs(args, 2, lambda: self.trips2Error(operator))
        
        elif operator in quads:
            valid = self.testNumArgs(args, 3, lambda: self.quadsError(operator))
            if valid: self.parseQuad(operator, args)
        
        elif operator == 'open':
            errorFunc = lambda: self.openError()
            #double error
            valid = self.testNumArgs(args, 1, errorFunc) or self.testNumArgs(args, 2, errorFunc)
            if valid: self.parseOpen(operator, args)
            
        else:
            self.manager.printInvalid()
        




