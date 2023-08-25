#ifndef LEXER_H
#define LEXER_H

#include <iostream>
#include <vector>
using namespace std;

enum TokenType { TEXT = 0, TAG = 1 };

struct Token {
    string text;
    TokenType type;

    Token(string t, TokenType ty);
};

// Tokenizes the given HTTP body into tags ("<p>", "</p>") and text ("hello")
vector<Token> lex(string body);

/**
 * Composite design pattern; element represents a node in the parsed HTML tree
 */
class Element {
   public:
    string text;
    Element* parent;
    virtual string toString();
};

class TextElement : public Element {
    TextElement(string t, Element* p);
};

class TagElement : public Element {
    vector<Element*> children;
    map<string, string> attributes;
    TagElement(string t, map<string, string> attr, Element* p);
};

/**
 * An non-leaf element node (open and close tag) that contains zero or multiple
 * children elements
 */
struct Element {
    string tag;
    vector<Element*> children;
    map<string, string> attributes;
    Element* parent;

    Element(string t, map<string, string> attr, Element* p);
    string toString();
};

/**
 * A leaf-node text element (e.g. the "abcd" in <p>"abcd"</p>)
 */
struct Text {
    string text;
    Element* parent;

    Text(string t, Element* p);
    string toString();
};

class HTMLParser {
   public:
    // Reads the tokens of the body and updates the unfinished list of tags
    // Returns the root element of the HTML page
    Element* parse();
    HTMLParser(string body);

   private:
    vector<Element*> unfinished;

    // Adds the current text or tag Element to the tree
    void add_text(string text);
    void add_tag(string tag);

    // Convert the incomplete tree (<h1><p>unfinished) to a complete tree by
    // closing off the open tags. Returns the root element of the HTML page
    Element* finish();

    // Returns the pair {tag, attributes} for a tag, e.g. <meta name="abcd">
    static pair<string, map<string, string>> getAttributes(string text);

    // The raw HTML string to parse
    string body;
};

void print_tree(Element* root, int indent = 0);

const vector<string> selfClosingTags = {
    "area",  "base", "br",   "col",   "embed",  "hr",    "img",
    "input", "link", "meta", "param", "source", "track", "wbr",
};

#endif