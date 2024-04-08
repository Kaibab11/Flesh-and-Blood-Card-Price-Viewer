from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QCompleter, QCheckBox, QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView
from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtGui import QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import urllib.request
import psycopg2

# Dictionary mapping edition and foiling codes to their corresponding names
string_to_list = {
    "1st Edition Normal": ["F", "S"],
    "1st Edition Rainbow Foil": ["F", "R"],
    "1st Edition Cold Foil": ["F", "C"],
    "Unlimited Edition Normal": ["U", "S"],
    "Unlimited Edition Rainbow Foil": ["U", "R"],
    "Normal": ["N", "S"],
    "Rainbow Foil": ["N", "R"],
    "Cold Foil": ["N", "C"]
}

pitch_to_color = {
    '1' : "Red", 
    '2' : "Yellow",
    '3' : "Blue"
}

color_to_pitch = {
    "Red" : '1',
    "Yellow" : '2',
    "Blue" : '3'

}

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Price Data Plotter')

        self.card_name_label = QLabel('Card Name:')
        self.card_name_input = QLineEdit()

        # Create a completer object with an empty list initially
        self.card_completer = QCompleter([])
        # Set case sensitivity and completion mode
        self.card_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # Set case insensitivity
        self.card_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        # Assign the completer to the card name input field
        self.card_name_input.setCompleter(self.card_completer)

        self.populate_set_button = QPushButton('Populate Sets and Colors')
        self.populate_set_button.clicked.connect(self.populate_setandcolor_combobox)

        self.set_label = QLabel('Set:')
        self.set_combobox = QComboBox()
        # Set minimum width for the combobox
        self.set_combobox.setMinimumWidth(200)

        self.color_label = QLabel('Color:')
        self.color_combobox = QComboBox()
        # Set minimum width for the combobox
        self.color_combobox.setMinimumWidth(200)

        self.plot_button = QPushButton('Plot')
        self.plot_button.clicked.connect(self.plot_data)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align the image to the center

        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        # Create checkboxes for each entry in string_to_list dictionary
        self.checkboxes = []
        for label in string_to_list.keys():
            checkbox = QCheckBox(label)
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)

        self.checkbox_layout = QHBoxLayout()

        # Add checkboxes to the layout
        for checkbox in self.checkboxes:
            self.checkbox_layout.addWidget(checkbox)


        # Layout for card name label and input
        self.card_name_layout = QHBoxLayout()
        self.card_name_layout.addWidget(self.card_name_label)
        self.card_name_layout.addWidget(self.card_name_input)

        # Layout for set label and combobox
        self.set_layout = QHBoxLayout()
        self.set_layout.addWidget(self.set_label)
        self.set_layout.addWidget(self.set_combobox)

        # Layout for set label and combobox
        self.colorbox_layout = QHBoxLayout()
        self.colorbox_layout.addWidget(self.color_label)
        self.colorbox_layout.addWidget(self.color_combobox)

        # Layout for Card Name and Set
        self.cardSet_layout = QHBoxLayout()
        self.cardSet_layout.addLayout(self.card_name_layout)
        self.cardSet_layout.addLayout(self.colorbox_layout)
        self.cardSet_layout.addLayout(self.set_layout)

        # Horizontal layout for image and graph
        self.image_graph_layout = QHBoxLayout()
        self.image_graph_layout.addWidget(self.image_label)
        self.image_graph_layout.addWidget(self.canvas)

        #Upper Layout
        self.upper_layout = QVBoxLayout()
        self.upper_layout.addLayout(self.cardSet_layout)
        self.upper_layout.addWidget(self.populate_set_button)
        self.upper_layout.addWidget(self.plot_button)
        self.upper_layout.addLayout(self.checkbox_layout)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.upper_layout)
        self.layout.addLayout(self.image_graph_layout)


        self.setLayout(self.layout)

        self.populate_card_completer()  # Populate card name completer initially

    def populate_card_completer(self):
        # Connect to the database and fetch unique card names
        conn = psycopg2.connect(
            dbname="FaB_Cards",
            user="",
            password="",
            host="",
            port=""
        )
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT name
            FROM cards
        """

        cursor.execute(query)
        cards = cursor.fetchall()

        cursor.close()
        conn.close()

        # Extract card names from the fetched data and set them as suggestions for the completer
        card_names = [card[0] for card in cards]
        self.card_completer.setModel(QStringListModel(card_names))

    def populate_setandcolor_combobox(self):
        card_name = self.card_name_input.text()

        # Connect to the database and fetch sets for the specified card
        conn = psycopg2.connect(
            dbname="FaB_Cards",
            user="",
            password="",
            host="",
            port=""
        )
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT s.name
            FROM sets s
            JOIN set_printings sp ON s.unique_id = sp.set_unique_id
            JOIN card_printings cp ON sp.unique_id = cp.set_printing_unique_id
            JOIN cards c ON cp.card_unique_id = c.unique_id
            WHERE c.name = %s
        """

        cursor.execute(query, (card_name,))
        sets = cursor.fetchall()

        query = """
            SELECT DISTINCT c.name AS card_name, c.pitch
            FROM cards c
            JOIN card_printings cp ON c.unique_id = cp.card_unique_id
            WHERE c.name = %s;
            """

        cursor.execute(query, (card_name,))
        pitchvalues = cursor.fetchall()
        cursor.close()
        conn.close()

        # Clear previous items and add fetched sets to the combobox
        self.set_combobox.clear()
        for set_name in sets:
            self.set_combobox.addItem(set_name[0])

        self.color_combobox.clear()
        for pitchvalue in pitchvalues:
            if pitchvalue[1] != "":
                self.color_combobox.addItem(pitch_to_color[pitchvalue[1]])

    def fetch_price_data(self, card_name, set_name, edition, foiling, pitch):
        # Connect to the database and fetch data
        conn = psycopg2.connect(
            dbname="FaB_Cards",
            user="",
            password="",
            host="",
            port=""
        )
        cursor = conn.cursor()

        query = """
            SELECT date_trunc('day', cp.date) AS day, AVG(cp.price) AS avg_price
            FROM card_prices cp
            JOIN card_printing_prices cpp ON cp.id = cpp.card_price_id
            JOIN card_printings cpr ON cpp.card_printing_id = cpr.unique_id
            JOIN cards c ON cpr.card_unique_id = c.unique_id
            JOIN set_printings sp ON cpr.set_printing_unique_id = sp.unique_id
            JOIN sets s ON sp.set_unique_id = s.unique_id
            WHERE c.name = %s
            AND s.name = %s
            AND cpr.edition = %s
            AND cpr.foiling = %s
        """

        # If pitch is provided, include it in the WHERE clause
        if pitch != None:
            query += " AND c.pitch = %s"

        query += """
            GROUP BY day
            ORDER BY day;
        """

        # Depending on whether pitch is provided, adjust the parameter tuple accordingly
        if pitch != None:
            cursor.execute(query, (card_name, set_name, edition, foiling, pitch))
        else:
            cursor.execute(query, (card_name, set_name, edition, foiling))

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return rows
    
    def load_image_from_url(self, url):
        # Load image from URL using urllib and QPixmap
        data = urllib.request.urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        # Scale down the image with smoothing
        max_width = 400
        max_height = 400
        scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return scaled_pixmap

    
    def plot_data(self):
        card_name = self.card_name_input.text()
        set_name = self.set_combobox.currentText()
        pitch = color_to_pitch[self.color_combobox.currentText()] if self.color_combobox.currentText() != "" else None

        # Check if a set is selected
        if set_name == "Select Set":
            print("Please select a set.")
            return

        self.figure.clear()

        # Connect to the database and fetch card data
        conn = psycopg2.connect(
            dbname="FaB_Cards",
            user="",
            password="",
            host="",
            port=""
        )
        cursor = conn.cursor()

        # Query the image URL of the selected card
        query_image = """
            SELECT cp.image_url
            FROM card_printings cp
            JOIN cards c ON cp.card_unique_id = c.unique_id
            JOIN set_printings sp ON cp.set_printing_unique_id = sp.unique_id
            JOIN sets s ON sp.set_unique_id = s.unique_id
            WHERE c.name = %s
            AND s.name = %s
        """

        # If pitch is provided, include it in the WHERE clause
        if pitch != None:
            query_image += " AND c.pitch = %s"

        query_image += " LIMIT 1"  # Add LIMIT 1 to the end of the query

        # Depending on whether pitch is provided, adjust the parameter tuple accordingly
        if pitch != None:
            cursor.execute(query_image, (card_name, set_name, pitch))
        else:
            cursor.execute(query_image, (card_name, set_name))

        result = cursor.fetchone()
        image_url = result[0] if result else None

        cursor.close()
        conn.close()

        # Load the image using QPixmap
        if image_url:
            pixmap = self.load_image_from_url(image_url)
            self.image_label.setPixmap(pixmap)

        ax = self.figure.add_subplot(111)

        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                label = checkbox.text()
                edition, foiling = string_to_list[label]
                price_data = self.fetch_price_data(card_name, set_name, edition, foiling, pitch)
                if price_data:
                    dates = [row[0] for row in price_data]
                    prices = [row[1] for row in price_data]

                    ax.plot(dates, prices, label=label, marker='o', linestyle='-', linewidth=2, alpha=0.8)


        ax.set_title('Price Data Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('AVG Price in dollars')
        ax.tick_params(axis='x')

        # Format x-axis date labels
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %d, %y'))

        ax.legend()
        ax.grid(True)

        self.canvas.draw()
