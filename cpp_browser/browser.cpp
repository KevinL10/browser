#include <gtkmm.h>

#include <iostream>

#include "layout.h"
#include "lexer.h"
#include "request.h"

class MyWindow : public Gtk::Window {
   public:
    MyWindow();
    Gtk::TextView m_TextView;
    Gtk::ScrolledWindow m_ScrolledWindow;
};

MyWindow::MyWindow() {
    set_title("Browser");
    set_default_size(800, 600);

    m_ScrolledWindow.set_policy(Gtk::PolicyType::EXTERNAL,
                                Gtk::PolicyType::AUTOMATIC);
    set_child(m_ScrolledWindow);

    HttpResponse response =
        sendGetRequest("https://browser.engineering/examples/xiyouji.html");
    auto refTextBuffer = Gtk::TextBuffer::create();

    vector<Token> tokens = lex(response.body);
    vector<LayoutElement> elements = layout(tokens);

    auto iter = refTextBuffer->get_iter_at_offset(0);
    for (LayoutElement element : elements) {
        iter = refTextBuffer->insert_with_tag(iter, element.text,
                                              element.toTextTag(refTextBuffer));
    }

    m_TextView.set_buffer(refTextBuffer);
    m_TextView.set_editable(false);
    m_TextView.set_cursor_visible(false);
    m_TextView.set_wrap_mode(Gtk::WrapMode::WORD);
    m_ScrolledWindow.set_child(m_TextView);
}

int main(int argc, char* argv[]) {
    auto app = Gtk::Application::create("org.gtkmm.examples.base");

    return app->make_window_and_run<MyWindow>(argc, argv);
}