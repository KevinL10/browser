#include <iostream>
#include <vector>

#include "lexer.h"

using namespace std;

Token::Token(string t, TokenType ty): text(t), type(ty) {}

vector<Token> lex(string body){
    vector<Token> out;
    string text = "";
    bool in_tag = false;

    for(char c: body){
        if(c == '<'){
            in_tag = true;
            if(!text.empty()) out.push_back(Token(text, TEXT));
            text = "";
        } else if(c == '>'){
            in_tag = false;
            out.push_back(Token(text, TAG));
            text = "";
        } else{
            text += c;
        }
    }

    if(!in_tag && !text.empty()){
        out.push_back(Token(text, TEXT));
    }
    return out;
}