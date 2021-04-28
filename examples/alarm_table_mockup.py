from qtpy.QtWidgets import *
from qtpy.QtCore import *

headers = ["Name", "Value", "Timestamp", "Severity", "Message","Tickets", "Area", "Subsystem"]
rows = [("DEMO:PV1", "6.0", "2021-03-08 8:20:00", "OK", "NO_ALARM", "", "", "Temp"), ("DEMO:PV2", "6.0", "2021-03-08 8:20:00", "MAJOR", "HIHI_ALARM", "", "", "Temp")]

class TableModel(QAbstractTableModel):
    def rowCount(self, parent):
        return len(rows)
    def columnCount(self, parent):
        return len(headers)
    def data(self, index, role):
        if role != Qt.DisplayRole:
            return QVariant()
        return rows[index.row()][index.column()]
    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return QVariant()
        return headers[section]

app = QApplication([])
model = TableModel()
view = QTableView()
view.setModel(model)
view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
view.setSortingEnabled(True)
view.show()
app.exec_()