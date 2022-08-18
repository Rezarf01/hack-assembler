#!/usr/bin/python3.1

import sys
import os
import subprocess
from parser import Parser
from code import Code
from symbol_table import SymbolTable

class Assembler:

    VAR_ADDRESS = 16 # starting memory address for variables

    def __init__(self, lines: list, path):
        self.current_var_address = self.VAR_ADDRESS
        self.path = path
        self.parser = Parser(lines)
        self.code = Code()
        self.symbol_table = SymbolTable()

    @staticmethod
    def read_file(path):
        try:
            f = open(path, 'r')
        except OSError as e: # directory/file doesn't exist
            raise Exception('Path supplied doesn\'t exist')
        else:
            source = f.readlines() 
            f.close()
            return source 

    def write_ins(self, ins):
        output = ins + '\n'
        filename = os.path.splitext(os.path.basename(self.path))[0] + '.hack'
        dirname = os.path.dirname(self.path)
        with open(f'{os.path.join(dirname, filename)}', 'a') as f:
            f.write(output)

    def main_loop(self):
        """ main parser loop. processes each line"""
        current_pass = 1
        while current_pass <= 2:

            if self.parser.hasMoreLines():
                self.parser.advance() # move to next line whilst ignoring comments
            else:
                self.parser.reset()
                current_pass += 1
                continue

            if current_pass == 1: # first pass
                self.first_pass()

            if current_pass == 2: # second pass
                self.second_pass()
        
    def first_pass(self):
        if self.parser.instructionType() == Parser.L_INSTRUCTION:
            symbol = self.parser.symbol()
            address = str(self.parser.line_number + 1)
            self.symbol_table.addEntry(symbol, address)

    def second_pass(self):
        binary_ins = None
        if self.parser.instructionType() == Parser.A_INSTRUCTION:

            symbol = self.parser.symbol()

            if symbol.isnumeric():
                d_address = symbol # in decimal

            else: # symbol

                if self.symbol_table.contains(symbol):
                    d_address = self.symbol_table.getAddress(symbol) # address in decimal
                else:
                    self.symbol_table.addEntry(symbol, self.current_var_address)
                    d_address = self.symbol_table.getAddress(symbol)
                    self.current_var_address += 1 # increment memory address for variables


            b_address = format(int(d_address), '015b') # convert to 15-bit binary format
            binary_ins = '0' + b_address


        if self.parser.instructionType() == Parser.C_INSTRUCTION:
            dest = self.code.dest(self.parser.dest())
            comp = self.code.comp(self.parser.comp())               
            jump = self.code.jump(self.parser.jump())

            binary_ins = '111' + comp + dest + jump


        if binary_ins:
            self.write_ins(binary_ins)
            binary_ins = None
       

def main():    
    args = sys.argv
    try:
        path = args[1]
    except IndexError:
        raise Exception('A path to hack assembly source file must be supplied')
    else:
        root,ext = os.path.splitext(path)
        if ext == '.asm':
            source = Assembler.read_file(path)
            a = Assembler(source, path)
            a.main_loop()
        else:
            raise Exception(f"{os.path.basename(path)} contains invalid file extension ({ext}).\n .asm extension is mandatory")


if __name__ == '__main__':
    try:
        subprocess.run(['stty', '-echo'], check=True)
        main()
    except BaseException as e:
        print('-'*50)
        print(e)
        print('-'*50)
    else:
        print('-'*50)
        print('Successfully created .hack file in source directory')
        print('-'*50)
    finally:
        subprocess.run(['stty', 'echo'], check=True)
        sys.exit(1)


