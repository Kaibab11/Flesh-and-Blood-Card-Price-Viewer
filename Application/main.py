from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
import sys
from Application.widgets.plot_widget import PlotWidget
from Application.widgets.statistics_widget import StatisticsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flesh-and-Blood Card Price Analyzer")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.plot_tab = PlotWidget()
        self.stats_tab = StatisticsWidget()
        self.tabs.addTab(self.plot_tab, "Plot Card Data")
        self.tabs.addTab(self.stats_tab, "Price Statistics")
        # Set stylesheets for the tabs
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane { /* The tab widget frame */
                border-top: 2px solid #aaaaaa; /* Light gray border on top of the tab widget */
            }

            QTabBar::tab:selected { /* Selected tab */
                background-color: #cccccc; /* Light gray background color for selected tab */
                color: black; /* Text color for selected tab */
            }

            QTabBar::tab:!selected { /* Unselected tab */
                background-color: #dddddd; /* Lighter gray background color for unselected tab */
                color: black; /* Text color for unselected tab */
            }
            """
        )

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 650)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
