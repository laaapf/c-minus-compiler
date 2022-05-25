from .token import Token, TokenType
from typing import Tuple
from enum import Enum


class LexError(Exception):
    def __init__(self, message="LexError"):
        self.message = message
        super().__init__(message)
    pass


class LexState(Enum):
    SPACE = 1
    IDENTIFIER = 2
    NUMBER = 3
    OPERATOR = 4
    COMPARATOR = 4
    DELIMITER = 5
    COMMENT = 6
    ERROR = 8


class Lex:

    def __init__(self):

        self.state = LexState.SPACE
        self.LETTER = [c for c in "qwertyuiopasdfghjklzxcvbnm"]
        self.NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.OPERATOR = ['+', '-', '*', '/']
        self.COMPARATOR = ['<', '>', '=', '!']
        self.DELIMITER = [';', ',', '(', ')', '[', ']', '{', '}']

    def get_tokens_from_file(self, filename: str):
        with open(filename, 'rt') as file:
            for idx, line in enumerate(file.readlines()):
                for token in self.get_tokens(line, idx+1):
                    yield token

    def get_tokens(self, source: str, line: str):
        i = 0
        add, token = self.get_token(source[i:], line)

        i += add
        while token.get_type() != TokenType.EOF and i < len(source):
            yield token
            add, token = self.get_token(source[i:], line)
            if token is None:
                return
            i += add
        yield token

    def get_token(self, source: str, line: int) -> Tuple[int, Token]:
        token = ''
        i = 0
        for idx, c in enumerate(source):
            next_c = ''
            if idx < len(source)-1:
                next_c = source[idx+1]
            if self.state == LexState.SPACE:
                if c.lower() in self.LETTER:
                    token += c
                    self.state = LexState.IDENTIFIER
                elif c == '0':
                    if next_c in self.NUMBER:
                        raise LexError(f"ERRO NA LINHA {line}\n\tO numero não pode comecar com 0")
                    token += c
                    i += 1
                    self.state = LexState.SPACE
                    return (i, Token(token, TokenType.NUMBER))
                elif c in self.NUMBER:
                    token += c
                    self.state = LexState.NUMBER
                elif c == '/' and next_c == '*':
                    i += 2
                    token += c
                    token += next_c
                    self.state = LexState.COMMENT
                    return (i, Token(token, TokenType.COMMENT))
                elif c in self.DELIMITER:
                    token += c
                    i += 1
                    self.state = LexState.SPACE
                    return (i, Token(token))
                elif c in self.OPERATOR:
                    token += c
                    i += 1
                    self.state = LexState.SPACE
                    return (i, Token(token))
                elif c in self.COMPARATOR:
                    token += c
                    self.state = LexState.COMPARATOR

            elif self.state == LexState.IDENTIFIER:
                if c.lower() in self.LETTER or c in self.NUMBER:
                    token += c
                else:
                    self.state = LexState.SPACE
                    return (i, Token(token, TokenType.IDENTIFIER))

            elif self.state == LexState.NUMBER:
                if c.lower() in self.LETTER:
                    self.state = LexState.ERROR
                    raise LexError(f'ERRO NA LINHA {line}\n\tO numero {token} não pode ser seguido por {c}.')
                elif c in self.NUMBER:
                    token += c
                    self.state = LexState.NUMBER
                else:
                    self.state = LexState.SPACE
                    return (i, Token(token, TokenType.NUMBER))

            elif self.state == LexState.COMPARATOR:
                if c == '=':
                    token += c
                    i += 1
                    self.state = LexState.SPACE
                    return (i, Token(token))
                elif c in self.COMPARATOR or c in self.OPERATOR or c in [',', ';']:
                    self.state = LexState.ERROR
                    raise LexError(f'ERRO NA LINHA {line}\n\tO comparador {token+c} é inválido .')
                else:
                    self.state = LexState.SPACE
                    return (i, Token(token))

            elif self.state == LexState.COMMENT:
                if c == '*' and next_c == '/':
                    self.state = LexState.SPACE
                    i += 2
                    token += c
                    token += next_c
                    return (i, Token(token, token_type=TokenType.COMMENT))
                else:
                    token += c
            i += 1
        if self.state == LexState.COMMENT:
            return (len(token), Token(token, TokenType.COMMENT))
        return (i, None)

