import csv

with open("LL1.csv") as f:
    LL1 = list(csv.reader(f))
    for i in range(1, len(LL1)):
        LL1[i][0] = f"<{LL1[i][0]}>"

with open("productions.txt") as f:
    productions = []

    for line in f:
        split = line.split(" ::= ")
        non_terminal = split[0].strip()
        items = split[1].strip().split(" ")
        productions.append([non_terminal, items])

class Parser:
    def __init__(self):
        self.Stack = ["$", productions[0][0]]
        self.Errors = []
        self.Output = []
    
    def Parse(self, token, lexeme, line_no):
        #print(f"\nStack: {self.Stack}")

        tos = self.Stack[-1]

        while tos == "epsilon":
            self.Stack.pop()
            tos = self.Stack[-1]
        
        #print(f"Stack after epsilon removal: {self.Stack}")

        if token == "INTEGER" or token == "DBL" or token == "ID":
            column = token.lower()
        else:
            column = lexeme

        #print(f"Column: {column}")
        
        while tos[0] == "<" and tos[-1] == ">":
            # Non-terminal
            column_num = -1
            for i in range(len(LL1[0])):
                if LL1[0][i] == column:
                    column_num = i
                    break
            
            if column_num == -1:
                # Invalid?
                #self.Errors.append("Invalid column")
                print(f"Invalid column: {LL1[0]}")
                return False
            
            row_num = -1
            for i in range(len(LL1)):
                if LL1[i][0] == tos:
                    row_num = i
                    break
            
            if row_num == -1:
                self.Errors.append("Invalid row")
                return False
            
            production_num = LL1[row_num][column_num]

            if production_num == "":
                # No production for (row, column)
                self.Errors.append(f"Unexpected '{lexeme}' on line {line_no}")
                return False
            
            production_num = int(production_num) - 1

            if 0 <= production_num < len(productions):
                # Valid production
                self.Stack.pop()
                current_production = productions[production_num]
                #print(current_production)
                for i in range(len(current_production[1])):
                    self.Stack.append(current_production[1][-i-1])
                tos = self.Stack[-1]
                #print(f"Stack: {self.Stack}")
                while tos == "epsilon":
                    self.Stack.pop()
                    tos = self.Stack[-1]
            else:
                # No production with such length..?
                return False
        
        # Reached a terminal
        if tos != column:
            # Error
            self.Errors.append(f"Unexpected '{lexeme}' on line {line_no}")
            #print(f"Wrong terminal: {column}")
            return False
        else:
            self.Stack.pop()
            if column == "id":
                self.Output.append(f"line {line_no:<3} | {lexeme}")
        
        return True

