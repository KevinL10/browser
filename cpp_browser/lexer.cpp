#include "lexer.h"

#include <algorithm>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
#include <iterator>

#include "utils.h"

using namespace std;

Element::~Element() {}

TextElement::TextElement(string text_, Element* parent_) {
    this->text = text_;
    this->parent = parent_;
}

string TextElement::toString() { return text; }

TagElement::TagElement(string text_, map<string, string> attr_,
                       Element* parent_) {
    this->text = text_;
    this->attributes = attr_;
    this->parent = parent_;
}

string TagElement::toString() { return "<" + text + ">"; }

// prints out the HTML tree
void print_tree(Element* node, int indent) {
    cout << string(indent, ' ') << node->toString() << "\n";
    for (Element* child : node->children) {
        print_tree(child, indent + 2);
    }
}

Element* HTMLParser::parse() {
    vector<Element> out;
    string text = "";
    bool in_tag = false;

    for (char c : body) {
        if (c == '<') {
            in_tag = true;
            if (!text.empty()) add_text(text);
            text = "";
        } else if (c == '>') {
            in_tag = false;
            add_tag(text);
            text = "";
        } else {
            text += c;
        }
    }

    if (!in_tag && !text.empty()) {
        add_text(text);
    }
    return finish();
}

HTMLParser::HTMLParser(string b) { body = b; }

void HTMLParser::add_text(string text) {
    // Ignore whitespace/newlines between consecutive tags
    if (trim(text).empty()) return;

    Element* parent = unfinished.back();
    Element* node = new TextElement(text, parent);
    parent->children.push_back(node);
}

void HTMLParser::add_tag(string tag) {
    // Ignore the <!doctype html> tag
    if (tag[0] == '!') return;

    map<string, string> attributes;
    tie(tag, attributes) = getAttributes(tag);

    if (tag[0] == '/') {
        // If there's only one more tag, then there is no parent tag
        if (unfinished.size() == 1) return;
        Element* node = unfinished.back();
        unfinished.pop_back();
        Element* parent = unfinished.back();
        parent->children.push_back(node);
    } else if (find(SELF_CLOSING_TAGS.begin(), SELF_CLOSING_TAGS.end(), tag) !=
               SELF_CLOSING_TAGS.end()) {
        Element* parent = unfinished.back();
        Element* node = new TagElement(tag, attributes, parent);
        parent->children.push_back(node);
    } else {
        Element* parent = unfinished.size() ? unfinished.back() : nullptr;
        Element* node = new TagElement(tag, attributes, parent);
        unfinished.push_back(node);
    }
}

Element* HTMLParser::finish() {
    if (unfinished.size() == 0) {
        add_tag("html");
    }
    while (unfinished.size() > 1) {
        Element* node = unfinished.back();
        unfinished.pop_back();
        Element* parent = unfinished.back();
        parent->children.push_back(node);
    }
    Element* root = unfinished.back();
    unfinished.pop_back();
    return root;
}

pair<string, map<string, string>> HTMLParser::getAttributes(string text) {
    // split text by whitespace
    istringstream iss(text);
    vector<string> parts;
    copy(istream_iterator<string>(iss), istream_iterator<string>(),
         back_inserter(parts));
    // auto start = 0;
    // auto end = text.find(" ");
    // while (end != string::npos) {
    //     parts.push_back(text.substr(start, end - start));
    //     start = end + 1;
    //     end = text.find(" ");
    // }

    string tag = lower(parts[0]);

    map<string, string> attributes;
    for (unsigned int i = 1; i < parts.size(); i++) {
        auto delim = parts[i].find("=");
        if (delim != string::npos) {
            string key = parts[i].substr(0, delim);
            string value = parts[i].substr(delim + 1);
            if (value.length() > 2 && (value[0] == '\'' || value[0] == '"')) {
                value = value.substr(1, value.length() - 2);
            }
            attributes[lower(key)] = value;
        } else {
            attributes[lower(parts[i])] = "";
        }
    }

    return {tag, attributes};
}