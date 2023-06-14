#ifndef LAYOUT_H
#define LAYOUT_H

#include <gtkmm.h>
#include <iostream>
#include <vector>

#include "lexer.h"

using namespace std;

struct LayoutElement {
    string weight;
    string style;
    int size;
    string text;

    LayoutElement(string w, string s, int si, string t)
        : weight(w), style(s), size(si), text(t) {}


    Glib::RefPtr<Gtk::TextTag> toTextTag(Glib::RefPtr<Gtk::TextBuffer>);
};

vector<LayoutElement> layout(vector<Token> tokens);

#endif