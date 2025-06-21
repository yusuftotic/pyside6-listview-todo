import sys
import csv
import os
from PySide6.QtWidgets import (
	QApplication,
	QMainWindow,
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QListView,
	QLineEdit,
	QPushButton,
	QAbstractItemView
)
from PySide6.QtCore import (
	Qt,
	QAbstractListModel
)
from PySide6.QtGui import (
	QImage
)

current_directory = os.path.dirname(os.path.abspath(__file__))

data_csv_path = os.path.join(current_directory, "data.csv")

tick_path = os.path.join(current_directory, "tick-16x16.png")

tick = QImage(tick_path)

class TodoApp(QMainWindow):
	
	def __init__(self):
		super().__init__()
		self.setupUi()

		self.model = TodoModel()
		self.load()
		self.list_view.setModel(self.model)

		self.lineedit_todo.returnPressed.connect(self.add)
		self.button_add.pressed.connect(self.add)
		self.button_delete.pressed.connect(self.delete)
		self.button_complete.pressed.connect(self.complete)
		
		self.list_view.doubleClicked.connect(self.toggle_complete)




	def add(self):
		text = self.lineedit_todo.text().strip()
		if text:
			self.model.todos.append((False, text))
			self.model.layoutChanged.emit()

			self.lineedit_todo.clear()
			self.save()
	


	def delete(self):
		indexes = self.list_view.selectedIndexes()
		if indexes:
			index = indexes[0]

			del self.model.todos[index.row()]
			self.model.layoutChanged.emit()

			self.list_view.clearSelection()
			self.save()
	


	def complete(self):
		indexes = self.list_view.selectedIndexes()
		if indexes:
			index = indexes[0]
			row = index.row()

			status, text = self.model.todos[row]

			if status:
				self.list_view.clearSelection()
				return

			self.model.todos[row] = (True, text)

			self.model.dataChanged.emit(index, index)
			self.list_view.clearSelection()
			self.save()

	def toggle_complete(self, index):
		row = index.row()
		status, text = self.model.todos[row]
		self.model.todos[row] = (not status, text)
		self.model.dataChanged.emit(index,index)
		self.save()



	def load(self):
		try:
			with open(data_csv_path, "r", encoding="utf-8", newline="") as csvfile:
				reader = csv.reader(csvfile)
				headers = next(reader)

				todos = []
				for row in reader:
					status = True if row[0] == "True" else False
					text = row[1]
					todos.append((status, text))

				self.model.todos = todos

		except Exception:
			pass



	def save(self):
		with open(data_csv_path, "w", encoding="utf-8", newline="") as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(("Status", "Text"))
			writer.writerows(self.model.todos)



	def setupUi(self):
		self.setWindowTitle("Todo")
		self.setFixedSize(300, 400)

		central_widget = QWidget()
		self.setCentralWidget(central_widget)

		layout = QVBoxLayout()
		central_widget.setLayout(layout)

		layout_button_container = QHBoxLayout()

		self.lineedit_todo = QLineEdit("")
		self.lineedit_todo.setPlaceholderText("Enter a todo...")
		layout.addWidget(self.lineedit_todo)

		self.button_add = QPushButton("Add Todo")
		layout.addWidget(self.button_add)

		self.list_view = QListView()
		self.list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
		self.list_view.setStyleSheet("""
			QListView::item {
				padding: 3px;
				margin: 2px;
			}
		""")
		layout.addWidget(self.list_view)

		self.button_delete = QPushButton("Delete")
		layout_button_container.addWidget(self.button_delete)

		self.button_complete = QPushButton("Complete")
		layout_button_container.addWidget(self.button_complete)

		layout.addLayout(layout_button_container)




class TodoModel(QAbstractListModel):
	def __init__(self, *args, todos=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.todos = todos or []

	def data(self, index, role):
		if role == Qt.ItemDataRole.DisplayRole:
			_, text = self.todos[index.row()]
			return text
		
		if role == Qt.ItemDataRole.DecorationRole:
			status, _ = self.todos[index.row()]
			if status == True:
				return tick
	
	def rowCount(self, index):
		return len(self.todos)




if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = TodoApp()
	window.show()
	sys.exit(app.exec())