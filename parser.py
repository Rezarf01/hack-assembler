#!/usr/bin/python3.1
import re

class Parser:

	A_INSTRUCTION = 1
	C_INSTRUCTION = 2
	L_INSTRUCTION = 3

	# regex patterns
	patterns = {

	A_INSTRUCTION: r'(@)(?P<symbol>\S+)', # @xxx
	C_INSTRUCTION: [
	r'(?P<dest>M|D|DM|A|AM|AD|ADM)=(?P<comp>\S+);(?P<jump>\w+)', # dest=comp;jump 
	r'(?P<dest>M|D|DM|A|AM|AD|ADM)=(?P<comp>\S+)',# dest=comp
	r'(?P<comp>\S+);(?P<jump>\w+)' # comp;jump 
	],
	L_INSTRUCTION: r'\((?P<symbol>\S+)\)' # (xxx)

	}
	
	def __init__(self, lines):
		self.lines = self.format(lines)
		self.line_index = -1 # so that first advance is 0
		self.current_line = None
		self.line_number = -1
		self.current_match = None

	def reset(self):
		self.line_index = -1		
		self.current_line = None
		self.line_number = -1
		self.current_match = None

	def format(self, lines):
		""" removes all whitespaces or inline comments from lines """
		f_lines = []
		for line in lines:
			fline = line.replace(' ', '').replace('\n', '') # remove whitespaces
			if '//' in fline:
				fline = fline[:fline.index('/')] # remove inline comment
			if fline != '': # if line not empty
				f_lines.append(fline)
		return f_lines

	def hasMoreLines(self):
		if self.lines[self.line_index + 1:len(self.lines)]:
			return True
		return False

	def advance(self):
		""" moves to next instruction ignoring comments """
		self.line_index += 1
		self.current_line = self.lines[self.line_index]

		if self.current_line.startswith('//'):
			self.advance() # move to next line if comment
		else:
			if self.instructionType() != Parser.L_INSTRUCTION:
				self.line_number += 1

	def instructionType(self):
		# compare current line with regular expressions
		A_match = re.match(Parser.patterns[Parser.A_INSTRUCTION], self.current_line) 
		L_match = re.match(Parser.patterns[Parser.L_INSTRUCTION], self.current_line)

		for pattern in Parser.patterns[Parser.C_INSTRUCTION]:
			C_match = re.match(pattern, self.current_line)
			if C_match:
				C_match = C_match
				break

		if A_match:
			match = A_match
			ins = Parser.A_INSTRUCTION
		if C_match:
			match = C_match
			ins = Parser.C_INSTRUCTION
		if L_match:
			match = L_match
			ins = Parser.L_INSTRUCTION

		self.current_match = match 
		return ins

# A-instruction and L-instruction methods -------------------------------
	def symbol(self):
		symbol = self.current_match.group('symbol')
		return symbol

# C-instruction methods ------------------------------
	def dest(self):
		try:
			dest = self.current_match.group('dest')
		except IndexError: # dest is omitted
			return None
		return dest
		
	def comp(self):
		try:
			comp = self.current_match.group('comp')
		except IndexError: # comp is omitted
			return None
		return comp

	def jump(self):
		try:
			jump = self.current_match.group('jump')
		except IndexError: # jump is omitted
			return None
		return jump
				