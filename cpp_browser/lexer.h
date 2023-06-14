#ifndef LEXER_H
#define LEXER_H

#include <iostream>
using namespace std;

enum TokenType { TEXT = 0, TAG = 1 };

struct Token {
    string text;
    TokenType type;

    Token(string t, TokenType ty);
};


// Tokenizes the given HTTP body into tags ("<p>", "</p>") and text ("hello world")
vector<Token> lex(string body);
#endif