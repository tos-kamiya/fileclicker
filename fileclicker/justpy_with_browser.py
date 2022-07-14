import sys
import threading

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView


def justpy_with_browser(web_page_builder, host="127.0.0.1", port=8000):
    import justpy

    # run a web server thread as a daemon (automatic shutdown)
    server_thread = threading.Thread(
        target=justpy.justpy, args=(web_page_builder,), kwargs={"host": host, "port": port}, daemon=True
    )
    server_thread.start()

    # run a web browser to show the web page
    app = QApplication([sys.argv[0]])
    web = QWebEngineView()
    web.load(QUrl("http://%s:%d/" % (host, port)))
    web.show()

    app.exec_()  # main loop


def sample_web_page_builder():
    import justpy as jp

    wp = jp.WebPage()
    d = jp.Div(a=wp, classes="m-3")

    c1 = "p-2 bg-blue-500 text-white rounded"
    c2 = "p-2 bg-white border-solid border-black border-2 rounded"
    c3 = "p-2 bg-red-500 text-white rounded"
    _r1 = jp.Span(text="Hello", classes=c1, a=d)
    _r2 = jp.Span(text="World", classes=c2, a=d)
    _r3 = jp.Span(text="!", classes=c3, a=d)

    return wp


if __name__ == "__main__":
    justpy_with_browser(sample_web_page_builder)
