class SemanticAnalyzer:
    def __init__(self):
        self.SymbolTable = [["global"]]
        self.Scope = 0
        self.Output = []
        self.Errors = []
    
    def EnterNewScope(self, scope_name):
        self.SymbolTable.append([scope_name])
        self.Scope = len(self.SymbolTable) - 1
    
    def ExitScope(self):
        self.SymbolTable.pop()
        self.Scope = len(self.SymbolTable) - 1
    
    def Add(self, list_of_values):
        list_of_values.insert(0, self.SymbolTable[self.Scope][0])

        if not self.__AddCheck(list_of_values):
            self.Errors.append(f"Multiple defined names '{list_of_values[1]}'")
        else:
            self.SymbolTable[self.Scope].append(list_of_values)
            self.Output.append(("-" * 4 * self.Scope + "> ") + "".join(v + "|" for v in list_of_values)[:-1])
    
    def __AddCheck(self, list_of_values):
        for i in range(1, len(self.SymbolTable[self.Scope])):
            if self.SymbolTable[self.Scope][i][2] == list_of_values[2]:
                return False
        
        return True
    
    def Find(self, lexeme, type=None):
        for i in range(len(self.SymbolTable) - 1, -1, -1):
            for j in range(1, len(self.SymbolTable[i])):
                if self.SymbolTable[i][j][2] == lexeme:
                    if type is None or self.SymbolTable[i][j][1] == type:
                        return True
        
        return False
