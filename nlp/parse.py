#!/usr/bin/python

import sys
import math


# This file contains an implementation of the Earley Parser

# weight is equal to the log(p)
# therefore, we wish to minimize the negative weight of the tree 
# or in this case, maximize the weight of the tree (because low probability rules result in a greater negative weights)
class rule:
	def __init__(self, _lhs, _rhs, _weight):
		self.lhs = _lhs
		self.rhs = _rhs
		self.weight = _weight

class state:
	def __init__(self, _rule, _column, _period, _weight, _bp):
		self.rule = _rule
		self.column = _column
		self.period = _period
		self.weight = _weight
		self.backpointer = _bp

	def toString(self):
		return "%-10s %-30s col: %-3d loc: %-3d wt: %-3.2f bp:%d" % (self.rule.lhs, str(self.rule.rhs), self.column, self.period, self.weight, len(self.backpointer))

	def toKey(self):
		return str(self.column) + "$" + str(self.period) + "$" + self.rule.lhs + "$" + str(self.rule.rhs)

class parser:

	def __init__ (self):
		self.grammar = {}
		self.chart = []
		self.chartkeys = [{}]
		self.predicted = [{}]

	def parse(self, sentence):
		words = sentence.split()

		for i in range(0, len(words) + 1):
			if i == len(self.chart):
				return
			for state in self.chart[i]:
				if self.incomplete(state):
					if self.nextCatIsNonTerminal(state):
						self.predict(state, i)
					else:
						if i < len(words):
							self.scan(state, i, words[i])
				else:
					self.complete(state, i)

	def predict(self, _state, index):
		if self.nextRule(_state) in self.predicted[index]:
			return
		else:
			self.predicted[index][self.nextRule(_state)] = True

		for rulei in self.grammar[self.nextRule(_state)]:
			s = state(rulei, index, 0, _state.weight + rulei.weight, [])
			if s.toKey() not in self.chartkeys[index]:
				self.chartkeys[index][s.toKey()] = s
				self.chart[index].append(s)
			elif self.chartkeys[index][s.toKey()].weight < s.weight:
				self.chartkeys[index][s.toKey()] = s

	def scan(self, _state, index, word):
		if self.nextRule(_state) == word:
			s = state(_state.rule, _state.column, _state.period + 1, _state.weight, _state.backpointer[:])
			if len(self.chart) == index + 1:
				self.predicted.append({})
				self.chart.append([])
				self.chartkeys.append({})
				self.chart[index + 1].append(s)
				self.chartkeys[index + 1][s.toKey()] = s
			elif self.chart[index + 1][0].weight < s.weight:
				self.chart[index + 1][0] = s

	def complete(self, _state, index):
		for statei in self.chart[_state.column]:
			if statei.period != len(statei.rule.rhs):
				if _state.rule.lhs == statei.rule.rhs[statei.period]:
					bp = statei.backpointer[:]
					bp.append(_state)
					s = state(statei.rule, statei.column, statei.period + 1, statei.weight, bp)
					if s.toKey() not in self.chartkeys[index]:
						self.chartkeys[index][s.toKey()] = s
						self.chart[index].append(s)
					elif self.chartkeys[index][s.toKey()].weight < s.weight:
						self.chartkeys[index][s.toKey()] = s

	def nextCatIsNonTerminal(self, _state):
		if self.nextRule(_state) not in self.grammar:
			return False
		else:
			return True

	def nextRule(self, _state):
		return _state.rule.rhs[_state.period]

	def incomplete(self, state):
		if state.period == len(state.rule.rhs):
			return False
		else:
			return True

	def initializeChart(self):
		rules = self.grammar["ROOT"]
		
		self.chart.append([])
		for rulei in rules:
			s = state(rulei, 0, 0, rulei.weight, [])
			self.chart[0].append(s)
			self.chartkeys[0][s.toKey()] = s

	def readGrammar(self, filename):
	 	rules = open(filename).read().splitlines() 

	 	for rulei in rules:
	 		if rulei.find('#') > -1:
	 			rulei = rulei[0:rulei.index('#')]

	 		rulei = rulei.strip().split()
	 		if len(rulei) > 0:
	 			prob = rulei.pop(0)
	 			lhs = rulei.pop(0)
	 			if lhs not in self.grammar:
	 				self.grammar[lhs] = []

	 			r = rule(lhs, rulei, math.log(float(prob))) 
	 			self.grammar[lhs].append(r)

	def buildParseTree(self, _state):
		
		tree = _state.rule.lhs
		for next_rule in _state.rule.rhs:
			if next_rule in self.grammar:
				for statei in _state.backpointer:
					if statei.rule.lhs == next_rule:
						tree += "(" + self.buildParseTree(statei) + ")"
						break
			else:
				tree += " " + next_rule
		return tree

	def buildParseTrees(self):
		lightestweight = state(None, None, None, -1 * float('inf'), None)
		success = False
		for statei in self.chart[len(self.chart) - 1]:
			if statei.rule.lhs == "ROOT":
	 			if lightestweight.weight < statei.weight:
	 				lightestweight = statei


	 	if lightestweight.weight != -1 * float('inf'):
		 	print "(" + self.buildParseTree(lightestweight) + ")"
		 	print lightestweight.weight
		else:
		 	print "failure"
	 	
def main():

	for sentence in open(sys.argv[2]).read().splitlines():
		p = parser()
		p.readGrammar(sys.argv[1])
		p.initializeChart()
		if len(sentence.strip()) != 0:
			p.parse(sentence)
			p.buildParseTrees()

main()