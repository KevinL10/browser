#include "layout.h"

#include <iostream>
#include <vector>

#include "lexer.h"
#include "utils.h"

using namespace std;

// TODO: cache the TextTag to avoid making duplicate
Glib::RefPtr<Gtk::TextTag> LayoutElement::toTextTag(
    Glib::RefPtr<Gtk::TextBuffer> refTextBuffer) {
    auto refTag = refTextBuffer->create_tag();
    if (style == "italic") {
        refTag->property_style() = Pango::Style::ITALIC;
    } else if (style == "bold") {
        refTag->property_weight() = Pango::Weight::BOLD;
    }

    refTag->property_size() = size * Pango::SCALE;
    return refTag;
}

// vector<LayoutElement> layout(vector<Token> tokens) {
//     vector<LayoutElement> out;
//     string weight = "normal";
//     string style = "roman";
//     int size = 12;

//     for (Token token : tokens) {
//         if (token.type == TEXT) {
//             out.push_back(LayoutElement(weight, style, size, trim(token.text)));
//         } else if (token.text == "i") {
//             style = "italic";
//         } else if (token.text == "/i") {
//             style = "roman";
//         } else if (token.text == "b") {
//             weight = "bold";
//         } else if (token.text == "/b") {
//             weight = "normal";
//         } else if (token.text == "small") {
//             size -= 2;
//         } else if (token.text == "/small") {
//             size += 2;
//         } else if (token.text == "big") {
//             size += 4;
//         } else if (token.text == "/big") {
//             size -= 4;
//         } else if (token.text == "br") {
//             // HACK: add new line for <br>
//             out.push_back(LayoutElement(weight, style, size, "\n"));
//             continue;
//         } else if (token.text == "/p") {
//             // HACK: add new line and indent after </p>
//             out.push_back(LayoutElement(weight, style, size, "\n\n"));
//         }
//     }

//     return out;
// }