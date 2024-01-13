import socket
import threading
import pyaudio
from PyQt5 import QtWidgets, QtGui, QtCore

HOST = 'localhost'
PORT = 5000
TEXT_PORT = 5001

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

google_font_css = """
@font-face {
    font-family: 'Montserrat';
    src: url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap');
}
"""

class VoiceCallWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.audio_stream = pyaudio.PyAudio()
        self.is_streaming = False
        self.is_muted = False
        self.setWindowTitle("Voice Chat")
        self.connect_button = QtWidgets.QPushButton("Connect")
        self.begin_voice_call_button = QtWidgets.QPushButton("Begin Voice Call")
        self.begin_voice_call_button.setEnabled(False)
        self.stop_voice_call_button = QtWidgets.QPushButton("Stop Voice Call")
        self.stop_voice_call_button.setEnabled(False)
        self.disconnect_button = QtWidgets.QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        self.status_label = QtWidgets.QLabel("Disconnected")
        self.status_label.setFixedSize(200, 30)  # Set a fixed size for the status label
        QtWidgets.QApplication.instance().setStyleSheet(google_font_css)
        self.mute_button = QtWidgets.QPushButton("Mute")
        self.mute_button.setVisible(False)

        # Use QGridLayout
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.connect_button, 0, 0)
        layout.addWidget(self.begin_voice_call_button, 1, 0)
        layout.addWidget(self.stop_voice_call_button, 2, 0)
        layout.addWidget(self.disconnect_button, 3, 0)
        layout.addWidget(self.status_label, 4, 0)
        layout.addWidget(self.mute_button, 5, 0)
        layout.setVerticalSpacing(5)

        self.setLayout(layout)
        self.connect_button.clicked.connect(self.connect)
        self.begin_voice_call_button.clicked.connect(self.begin_voice_call)
        self.stop_voice_call_button.clicked.connect(self.stop_voice_call)
        self.disconnect_button.clicked.connect(self.disconnect)
        self.mute_button.clicked.connect(self.toggle_mute)
        self.set_styles()

    def set_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #282a36;
                color: #f8f8f2;
            }
            QPushButton {
                background-color: #44475a;
                border-style: none;
                color: #f8f8f2;
                font: bold 15px;
                padding: 16px;
                width: 250px;
            }
            QLabel {
                font: bold 14px;
                color: #50fa7b;  /* Dracula green for the status label */
                text-align: middle;
            }
        """)



    def connect(self):
        if self.client_socket:
            return
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.status_label.setText("Connected")
        self.connect_button.setEnabled(False)
        self.begin_voice_call_button.setEnabled(True)
        self.stop_voice_call_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)

    def begin_voice_call(self):
        if self.is_streaming:
            return
        self.is_streaming = True
        threading.Thread(target=self._send_audio).start()
        threading.Thread(target=self._receive_audio).start()
        self.begin_voice_call_button.setEnabled(False)
        self.stop_voice_call_button.setEnabled(True)
        self.mute_button.setVisible(True)

    def stop_voice_call(self):
        self.is_streaming = False
        self.stop_voice_call_button.setEnabled(False)
        self.begin_voice_call_button.setEnabled(True)
        self.mute_button.setVisible(False)
        self.is_muted = False
        self.mute_button.setText("Mute")

    def disconnect(self):
        if not self.client_socket:
            return
        self.is_streaming = False
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()
        self.client_socket = None
        self.audio_stream.terminate()
        self.status_label.setText("Disconnected")
        self.connect_button.setEnabled(True)
        self.begin_voice_call_button.setEnabled(False)
        self.stop_voice_call_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_button.setText("Unmute")
        else:
            self.mute_button.setText("Mute")

    def _send_audio(self):
        stream = self.audio_stream.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        while self.is_streaming:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                if not self.is_muted:
                    self.client_socket.sendall(data)
            except (OSError, BrokenPipeError):
                break
        stream.stop_stream()
        stream.close()

    def _receive_audio(self):
        stream = self.audio_stream.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
        while self.is_streaming:
            try:
                data = self.client_socket.recv(CHUNK)
                stream.write(data)
            except (OSError, ConnectionResetError):
                break
        stream.stop_stream()
        stream.close()

class TextChatWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.text_socket.connect((HOST, TEXT_PORT))
        QtWidgets.QApplication.instance().setStyleSheet(google_font_css)
        self.setWindowTitle("Text Chat")
        self.chat_area = QtWidgets.QTextEdit()
        font = QtGui.QFont("Arial", 30)
        self.chat_area.setFont(font)
        self.text_edit = QtWidgets.QTextEdit()
        font = QtGui.QFont("Arial", 30)
        self.text_edit.setFont(font)
        self.text_edit.setMaximumHeight(100)
        self.send_button = QtWidgets.QPushButton("Send")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.chat_area)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.send_button)
        self.setLayout(layout)
        self.send_button.clicked.connect(self.send_text)
        self.set_styles()
        threading.Thread(target=self._receive_text).start()

    def set_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #282a36;
                color: #f8f8f2;
            }
            QPushButton {
                background-color: #44475a;
                border-style: none;
                color: #f8f8f2;
                font: bold 12px;
                padding: 8px;
                min-width: 100px;
            }
            QTextEdit {
                background-color: #44475a;  /* Darker color for the text area */
                border-style: none;
                color: #f8f8f2;
                font: 26px;
                font-family: 'Montserrat', sans-serif;
                padding: 8px;
            }
        """)
        self.chat_area.setReadOnly(True)
        self.chat_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chat_area.setAlignment(QtCore.Qt.AlignRight)

    def send_text(self):
        text = self.text_edit.toPlainText().strip()
        if text:
            encoded_text = text.encode()
            self.text_socket.sendall(encoded_text)
            self.add_message_to_chat("<b style='color: #409EFF;'>You: </b>" + text)
            self.text_edit.clear()

    def add_message_to_chat(self, message):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertHtml(message + "<br>")
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()

    def _receive_text(self):
        while True:
            try:
                data = self.text_socket.recv(1024)
                if not data:
                    break
                self.add_message_to_chat("<b style='color: #67C23A;'>Student 2: </b>" + data.decode())
            except (OSError, ConnectionResetError):
                break

class HomeWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FeynPrep")
        self.setGeometry(100, 100, 800, 600)

        # Container for the home page content
        self.home_page_container = QtWidgets.QWidget()
        self.home_page_layout = QtWidgets.QVBoxLayout(self.home_page_container)

        # Create a QLabel for the text
        self.text_label = QtWidgets.QLabel("""SynConnect""")
        font = QtGui.QFont("Arial", 24, QtGui.QFont.Bold)
        self.text_label.setFont(font)
        self.text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.text_label.setStyleSheet("color: #F5F5F5;")
        self.home_page_layout.addWidget(self.text_label)

#         self.problem_label = QtWidgets.QLabel("""The Problem""")
#         font = QtGui.QFont("'Montserrat', sans-serif", 20)
#         self.problem_label.setFont(font)
#         self.problem_label.setAlignment(QtCore.Qt.AlignLeft)
#         self.problem_label.setStyleSheet("font-family: 'Montserrat', sans-serif; color: #ff5e0e;")
#         self.home_page_layout.addWidget(self.problem_label)

#         self.problem_text = QtWidgets.QLabel("""Humans forget 50% of new information learned in 1 hour; 70% in 24 hours; 80% in 1 month. This is a 
# huge problem for millions of students who need to study for numerous exams around the year. This is 
# accentuated by inadequate and unorganized teaching resources without one-to-one interaction. Hence, the 
# students are unable to form a firm understanding of the concepts, which leads to doubts in their 
# foundational education. Therefore, most students don’t get the one-to-one attention to ask doubts and
# understand content properly.""")
        # font = QtGui.QFont("'Montserrat', sans-serif", 20)
        # self.problem_text.setFont(font)
        # self.problem_text.setAlignment(QtCore.Qt.AlignLeft)
        # self.problem_text.setStyleSheet("font-family: 'Montserrat', sans-serif; color: #b31928;")
        # self.home_page_layout.addWidget(self.problem_text)





        # Create a vertical spacer to push the image to the top
        self.vertical_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.home_page_layout.addItem(self.vertical_spacer)

        self.voice_call_window = VoiceCallWindow()
        self.text_chat_window = TextChatWindow()

        self.navbar = QtWidgets.QWidget()
        self.voice_call_button = QtWidgets.QPushButton("Voice Call")
        self.text_chat_button = QtWidgets.QPushButton("Text Chat")
        self.home_button = QtWidgets.QPushButton("Home")  # New button for the home page

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.navbar)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.stacked_widget.addWidget(self.home_page_container)  # Add home page container to the stacked widget
        self.stacked_widget.addWidget(self.voice_call_window)
        self.stacked_widget.addWidget(self.text_chat_window)
        layout.addWidget(self.stacked_widget)

        self.navbar_layout = QtWidgets.QHBoxLayout(self.navbar)
        self.navbar_layout.addWidget(self.home_button)  # Add the home button to the navbar
        self.navbar_layout.addWidget(self.voice_call_button)
        self.navbar_layout.addWidget(self.text_chat_button)

        self.home_button.clicked.connect(self.show_home_page)  # Connect the home button to the home page
        self.voice_call_button.clicked.connect(self.show_voice_call_window)
        self.text_chat_button.clicked.connect(self.show_text_chat_window)
        self.set_styles()
        self.show_home_page()  # Show the home page initially

        self.setLayout(layout)

    def show_home_page(self):
        self.stacked_widget.setCurrentWidget(self.home_page_container)

    def show_voice_call_window(self):
        self.stacked_widget.setCurrentWidget(self.voice_call_window)

    def show_text_chat_window(self):
        self.stacked_widget.setCurrentWidget(self.text_chat_window)
    
    def set_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #282a36;
                color: #f8f8f2;
            }
            QPushButton {
                background-color: #44475a;
                border-style: none;
                color: #f8f8f2;
                font: bold 16px;
                padding: 8px;
                min-width: 100px;
            }
        """)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    home_window = HomeWindow()
    home_window.showMaximized()
    app.exec_()
