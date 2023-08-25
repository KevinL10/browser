// #include "request.h"
// #include <gtk/gtk.h>
// using namespace std;

// int main(int argc, char **argv) {
//     if (argc > 2) {
//         cout << "Usage: ./browser <url>\n";
//         return 0;
//     }

//     string url = (argc == 1) ? "https://example.org" : argv[1];
//     HttpResponse httpResponse = sendGetRequest(url);

//     httpResponse.print();


//     gtk_init(&argc, &argv);

// }


#include <gtkmm.h>
#include <iostream>
#include "request.h"
class MyWindow : public Gtk::Window
{
public:
  MyWindow();

protected:
  Gtk::Button m_button;
  Gtk::TextView m_TextView;
  void on_button_clicked();
};

MyWindow::MyWindow()
:m_button("Hello World")
{
  set_title("Basic application");
  set_default_size(600, 400);
  // Sets the margin around the button.
  m_button.set_margin(10);

  // When the button receives the "clicked" signal, it will call the
  // on_button_clicked() method defined below.
  m_button.signal_clicked().connect(sigc::mem_fun(*this,
              &MyWindow::on_button_clicked));

  // This packs the button into the Window (a container).
  // set_child(m_button);


  auto refTagMatch = Gtk::TextBuffer::Tag::create();
  refTagMatch->property_background() = "orange";
  auto refTagTable = Gtk::TextBuffer::TagTable::create();
  refTagTable->add(refTagMatch);
  //Hopefully a future version of gtkmm will have a set_tag_table() method,
  //for use after creation of the buffer.
  auto refBuffer = Gtk::TextBuffer::create(refTagTable);
  refBuffer->insert(refBuffer->get_iter_at_offset(0), "abcd");

  auto regTextBuffer = Gtk::TextBuffer::create();
  regTextBuffer->set_text("this is some text");
  m_TextView.set_buffer(refBuffer);

  m_TextView.set_editable(false);
  m_TextView.set_cursor_visible(false);
  set_child(m_TextView);
  // auto refBuffer = m_View1.get_buffer();
  // Glib::RefPtr<Gtk::TextBuffer::Tag> refTag = refBuffer->create_tag("heading");
  // refTag->property_weight() = Pango::Weight::BOLD;
  // refTag->property_size() = 15 * Pango::SCALE;
  // auto iter = refBuffer->get_iter_at_offset(0);
  // refBuffer->insert(iter, "The text widget can display text with all kinds of nifty attributes. It also supports multiple views of the same buffer; this demo is showing the same buffer in two places.\n\n");
}

void MyWindow::on_button_clicked(){
  std::cout<<"Hello World\n";
  HttpResponse httpResponse = sendGetRequest("https://example.org/index.html");
  httpResponse.print();
}

int main(int argc, char* argv[])
{
  auto app = Gtk::Application::create("org.gtkmm.examples.base");

  return app->make_window_and_run<MyWindow>(argc, argv);
}