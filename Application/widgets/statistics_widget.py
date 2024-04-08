from PyQt6.QtWidgets import QWidget, QTableWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
import psycopg2
import datetime

list_to_string = {
    ("U", "S"): "Unlimited Edition Normal",
    ("U", "R"): "Unlimited Edition Rainbow Foil",
    ("F", "S"): "1st Edition Normal",
    ("F", "R"): "1st Edition Rainbow Foil",
    ("F", "C"): "1st Edition Cold Foil",
    ("N", "S"): "Normal",
    ("N", "R"): "Rainbow Foil",
    ("N", "C"): "Cold Foil"
}

pitch_to_color = {
    "1" : "Red", 
    "2" : "Yellow",
    "3" : "Blue"
}

class StatisticsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Card Name", "Color", "Foiling", "Set", "Last Week's Price", "Current Price", "% Change"])

        # Create buttons layout
        self.buttons_layout = QHBoxLayout()

        self.calculate_increase_button = QPushButton("Calculate Highest % Increase")
        self.calculate_increase_button.clicked.connect(self.calculate_highest_increase)

        self.calculate_decrease_button = QPushButton("Calculate Highest % Decrease")
        self.calculate_decrease_button.clicked.connect(self.calculate_highest_decrease)

        self.buttons_layout.addWidget(self.calculate_increase_button)
        self.buttons_layout.addWidget(self.calculate_decrease_button)

        # Define layout for the price statistics tab
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.buttons_layout)  # Add the buttons layout to the main layout
        self.setLayout(self.layout)  # Set the main layout for the window

    def calculate_highest_increase(self):
        rows = self.fetch_price_data_for_statistics()
        # Sort valid rows based on percentage increase
        rows.sort(key=lambda x: ((float(x[6]) - float(x[5])) / float(x[5])) * 100, reverse=True)
        # Display statistics for the sorted valid rows
        self.display_statistics(rows[:30])


    def calculate_highest_decrease(self):
        rows = self.fetch_price_data_for_statistics()
        # Sort valid rows based on percentage increase
        rows.sort(key=lambda x: ((float(x[6]) - float(x[5])) / float(x[5])) * 100)
        # Display statistics for the sorted valid rows
        self.display_statistics(rows[:30])

    def fetch_price_data_for_statistics(self):
        # Connect to the database and fetch data
        conn = psycopg2.connect(
            dbname="FaB_Cards",
            user="",
            password="",
            host="",
            port=""
        )
        cursor = conn.cursor()

        # Get the date ranges
        nine_days_ago = (datetime.datetime.now() - datetime.timedelta(days=9)).date()
        seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
        two_days_ago = (datetime.datetime.now() - datetime.timedelta(days=2)).date()
        today = datetime.datetime.now().date()

        query = """
            SELECT c.name, c.pitch, cpr.foiling, cpr.edition, s.name AS set_name, 
                AVG(CASE WHEN cp.date BETWEEN %s AND %s THEN cp.price ELSE NULL END) AS first_price,
                AVG(CASE WHEN cp.date BETWEEN %s AND %s THEN cp.price ELSE NULL END) AS last_price
            FROM card_prices cp
            JOIN card_printing_prices cpp ON cp.id = cpp.card_price_id
            JOIN card_printings cpr ON cpp.card_printing_id = cpr.unique_id
            JOIN cards c ON cpr.card_unique_id = c.unique_id
            JOIN set_printings sp ON cpr.set_printing_unique_id = sp.unique_id
            JOIN sets s ON sp.set_unique_id = s.unique_id
            GROUP BY c.name, cpr.foiling, cpr.edition, s.name, c.pitch
            HAVING ABS(AVG(CASE WHEN cp.date BETWEEN %s AND %s THEN cp.price ELSE NULL END) - 
                    AVG(CASE WHEN cp.date BETWEEN %s AND %s THEN cp.price ELSE NULL END)) >= 1
        """

        cursor.execute(query, (nine_days_ago, seven_days_ago, two_days_ago, today, 
                            nine_days_ago, seven_days_ago, two_days_ago, today))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return rows

    def display_statistics(self, rows):
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            card_name, pitch, foiling, edition, set_name, first_price, last_price = row
            foiling_edition = list_to_string.get((edition, foiling), "")
            color = pitch_to_color.get(pitch, None) if pitch != '' else None
            percent_change = ((float(last_price) - float(first_price)) / float(first_price)) * 100
            self.table.setItem(i, 0, QTableWidgetItem(card_name))
            self.table.setItem(i, 1, QTableWidgetItem(color))
            self.table.setItem(i, 2, QTableWidgetItem(foiling_edition))
            self.table.setItem(i, 3, QTableWidgetItem(set_name))
            self.table.setItem(i, 4, QTableWidgetItem(f"{first_price:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{last_price:.2f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{percent_change:.2f}%"))

        # Adjust column widths to fill the table widget
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
