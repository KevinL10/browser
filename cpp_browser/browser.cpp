#include <gtkmm.h>

#include <iostream>

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
    auto regTextBuffer = Gtk::TextBuffer::create();
    regTextBuffer->set_text(response.body);
    m_TextView.set_buffer(regTextBuffer);

    m_ScrolledWindow.set_child(m_TextView);
}

int main(int argc, char* argv[]) {
    auto app = Gtk::Application::create("org.gtkmm.examples.base");

    return app->make_window_and_run<MyWindow>(argc, argv);
}