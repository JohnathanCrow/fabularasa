from .windows.main_window import BookClubWindow

def main():
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = BookClubWindow()
    window.show()
    sys.exit(app.exec())