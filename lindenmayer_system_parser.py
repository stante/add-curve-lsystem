import re
import unittest
from collections import namedtuple

SYMBOL     = r'(?P<SYMBOL>[a-zA-Z])'
REPLACE    = r'(?P<REPLACE>\:=)'
DIRECTION  = r'(?P<DIRECTION>\+|\-)'
PUSH       = r'(?P<PUSH>\[)'
POP        = r'(?P<POP>\])'
WS         = r'(?P<WS>\s+)'

Token = namedtuple('Token', ['type', 'value'])

class LindenmayerSystemParser:
    parsed_sequence = []

    def __init__(self):
        self.pattern = re.compile('|'.join([SYMBOL, REPLACE, DIRECTION, PUSH, POP,  WS]))

    def _tokenize(self, string):
        for match in self.pattern.finditer(string):
            token = Token(match.lastgroup, match.group())
            if token.type != 'WS':
                yield token
        
    def _startover(self, string):
        self.tokens = self._tokenize(string)
        self.current_token = None
        self.next_token = None
        self.parsed_sequence = []

    def _advance(self):
        self.current_token, self.next_token = self.next_token, next(self.tokens, Token('EMPTY', 'EMPTY'))
        self.parsed_sequence.append(self.next_token)
  
    def _expect(self, symbol):
        if not self._accept(symbol):
            raise SyntaxError()

    def _accept(self, symbol):
        if self.next_token and self.next_token.type == symbol:
            self._advance()
            return True
        else:
            return False

    def _scanner(self, string):
        return self.pattern.scanner(string)

    def rule_valid(self, string):
        try:
            self.parse(string)
            return True
        except SyntaxError:
            return False

    def parse(self, string):
        self._startover(string)
        self._advance()

        # Apply start rule
        self._rule()
        
        return self.parsed_sequence
        
    def _rule(self):
        """rule ::= SYMBOL := movement"""
        if self._accept('SYMBOL'):
            if self._accept('REPLACE'):
                self._grow()
                if not self._accept("EMPTY"):
                    raise SyntaxError()
            else:
                raise SyntaxError()
        else:
            raise SyntaxError()

    def _grow(self):
        """order ::= DIRECTION order | [ order ] | SYMBOL order | SYMBOL"""

        if self._accept('DIRECTION'):
            self._grow()
        elif self._accept('SYMBOL'):
            self._grow()
        elif self._accept('PUSH'):
            self._grow()
            self._expect('POP')
            self._grow()
        else:
            pass

class TestParserFunctions(unittest.TestCase):
    def setUp(self):
        self.parser = LindenmayerSystemParser()

    def test_pattern_01(self):
        self.assertTrue(self.parser.rule_valid("F:=F"))

    def test_pattern_02(self):
        self.assertFalse(self.parser.rule_valid("F"))

    def test_pattern_03(self):
        self.assertTrue(self.parser.rule_valid("F:=F[F]F"))

    def test_pattern_04(self):
        self.assertFalse(self.parser.rule_valid("F:=F]"))

    def test_pattern_05(self):
        self.assertTrue(self.parser.rule_valid("F:="))
    

if __name__ == '__main__':
    unittest.main()
