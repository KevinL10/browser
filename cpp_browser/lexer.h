#ifndef LEXER_H
#define LEXER_H

#include <iostream>
#include <map>
#include <vector>
using namespace std;

/**
 * Composite design pattern; element represents a node in the parsed HTML tree
 */
class Element {
   public:
    virtual ~Element();

    virtual string toString() = 0;

    string text;
    Element* parent;

    // only the TextElement will have children, but we keep this instance
    // variable in the superclass for convenience
    vector<Element*> children;
};

// Text is a leaf-node (e.g. the "abcd" in <p> "abcd" </p>)
class TextElement : public Element {
   public:
    TextElement(string t, Element* p);

    virtual string toString() override;
};

// Tag is a non-leaf node that contains multiple children Elements
class TagElement : public Element {
   public:
    map<string, string> attributes;

    TagElement(string t, map<string, string> attr, Element* p);

    virtual string toString() override;
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

const vector<string> SELF_CLOSING_TAGS = {
    "area",  "base", "br",   "col",   "embed",  "hr",    "img",
    "input", "link", "meta", "param", "source", "track", "wbr",
};

#endif