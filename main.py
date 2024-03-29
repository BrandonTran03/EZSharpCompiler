import json
import csv
import os
from parse import LL1, productions, Parser
from semanticAnalyzer import SemanticAnalyzer

# Constants
BUFFER_SIZE = 2048
TOKEN_TYPES = [
    ("OPERATOR", [1, 2, 3, 4, 5, 7, 8, 9]),
    ("ASSIGN", [6]),
    ("ID", [10]),
    ("INTEGER", [11]),
    ("DBL", [13, 16]),
    ("DELIMITER", [17]),
    ("OPERATOR", [18])
]

# Global variables
buffer = ["", ""] # buffer 1 and buffer 2
current_buffer = 0
curr_char = 0
prev = 0
flag = 0

# Output stuff
output = ""
error_output = ""
line_no = 1

# Setting up keywords
with open("keywords.json") as f:
    keywords = json.load(f)

# Setting up transition table
with open("TT.csv") as f:
    TT = list(csv.reader(f))
    TT = TT[1:]
    for i in range(len(TT)):
        TT[i] = TT[i][1:]
    for i in range(len(TT)):
        for j in range(len(TT[i])):
            num = TT[i][j]
            if num == "":
                TT[i][j] = -1
            else:
                TT[i][j] = int(TT[i][j])

def getTokenType(state, token):
    """
    This function gets the gets the token-lexeme pair

    Args:
        state - The state that the token came from
        token - The actual token
    
    Returns:
        type - The token type (String)
    """

    for keyword in keywords:
        if token == keyword:
            return "KEYWORD"

    for tokenInfo in TOKEN_TYPES:
        for val in tokenInfo[1]:
            if val == state:
                return tokenInfo[0]
    
    return "No type"

# This function gets the next valid token, returns none if none
def getNextToken(f):
    """
    This function gets the next VALID token in the file
    Outputs to errorOuput.txt if any errors were found

    Args:
        f - The file to be read from
    
    Returns:
        token - The valid token that was found, None otherwise
    """

    global buffer, current_buffer, prev, curr_char, error_output, line_no, flag

    token = ""
    last_accepted_token = None
    prev = 0

    while True:
        if curr_char >= len(buffer[current_buffer]) or not buffer[current_buffer]:
            curr_char = 0
            current_buffer = (current_buffer + 1) % 2
            if flag == 0:
                buffer[current_buffer] = f.read(BUFFER_SIZE)
            else:
                flag = 0
            #print(buffer[current_buffer])
        
        if not buffer[current_buffer]:
            # Reached EOF
            return token.strip()
        
        # Looping until found finish state OR reject state
        while curr_char < len(buffer[current_buffer]):
            char = buffer[current_buffer][curr_char]
            ascii_char = ord(char)
            state = TT[prev][ascii_char]

            if state != -1:
                if state == 0:
                    return token.strip()
                
                token += char
                curr_char += 1
                prev = state

                if ascii_char == 10:
                    # new line
                    line_no += 1
                
                if TT[prev][32] == 0:
                    # Saving last accepted token and all the information attached to it just in case I need to revert back to it
                    last_accepted_token = (token, current_buffer, curr_char, prev, line_no)
            else:
                # Reject state, so we need to revert to the state of the last accepted token
                error_output += f"Unexpected symbol '{char}' on line {line_no}\n"
                if last_accepted_token is not None:
                    token, new_buffer, curr_char, prev, line_no = last_accepted_token

                    if new_buffer != current_buffer:
                        flag = 1
                    current_buffer = new_buffer

                    return token
                return None
                

def lexicalAnalysis(f):
    """
    This function performs the lexical analysis of the compiler
    Outputs results to output.txt

    Args:
        f - The file to be read from
    
    Returns:
        None
    """

    global output, LL1_parser, line_no, semantic_analyzer
    last_lexeme = None

    while True:
        token = getNextToken(f)

        # Checks if there was a token found
        if token is not None and token != "":
            token_type = getTokenType(prev, token)
            output += f"{token_type:10} | {token}\n"
            LL1_parser.Parse(token_type, token, line_no)

            if last_lexeme == "def":
                    semantic_analyzer.EnterNewScope()
            elif token_type == "ID":
                semantic_analyzer.Add([line_no, token, token_type, semantic_analyzer.Scope])
            
            last_lexeme = token
        
        # Reached EOF, so exit lexicalAnalysis
        if not buffer[current_buffer]:
            return

def main():
    global output, error_output, LL1_parser, semantic_analyzer

    #os.system("cls")
    
    LL1_parser = Parser()
    semantic_analyzer = SemanticAnalyzer()

    selection_str = "Which file would you like to compile?\n"
    test_files = os.listdir("./TestCases")
    for i,fName in enumerate(test_files):
        selection_str += f"{i+1}) {fName}\n"
    print(selection_str.strip())
    
    file_name = ""
    while not file_name:
        try:
            num = int(input("> "))
            if num <= len(test_files) and num >= 1:
                file_name = test_files[num - 1]
            else:
                raise Exception()
        except:
            print("Please enter a valid number")

    print()

    with open("./TestCases/" + file_name, "r") as f:
        lexicalAnalysis(f)
    
    with open("output.txt", "w") as f:
        f.write(output)
    
    with open("errorOutput.txt", "w") as f:
        f.write(error_output)
    
    with open("parsingOutput.txt", "w") as f:
        f.write("".join(v + "\n" for v in LL1_parser.Output))
    
    with open("parsingErrors.txt", "w") as f:
        f.write("".join(v + "\n" for v in LL1_parser.Errors))
    
    with open("semanticsOutput.txt", "w") as f:
        f.write("".join(v + "\n" for v in semantic_analyzer.Output))
    
    with open("semanticsErrors.txt", "w") as f:
        f.write("".join(v + "\n" for v in semantic_analyzer.Errors))

    print(f"Files updated! (Compiled: {file_name})")
    input("Press 'Enter' to close the program.")

if __name__ == "__main__":
    main()