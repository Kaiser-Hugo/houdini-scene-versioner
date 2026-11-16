from pathlib import Path

import hou
from PySide6 import QtWidgets, QtCore
from datetime import datetime

from core import (parse_scene_name, build_scene_folder, list_versions)

_history_window = None


def show_history():
	"""Pyside scene verion ecplorer"""
	global _history_window

	scene_name = hou.hipFile.basename()
	split_name = parse_scene_name(scene_name)
	if split_name is None:
		hou.ui.displayMessage("invalide scene name")
		return None

	shot, task, _ = split_name

	job = hou.getenv("JOB")
	if job is None:
		hou.ui.displayMessage("$JOB is not defined : impossible to save")
		return None
	folder = build_scene_folder(Path(job), shot, task)

	versions = list_versions(folder, shot, task)

	dialog = QtWidgets.QDialog(hou.qt.mainWindow())
	dialog.setWindowTitle(f"Historique - {shot} / {task}")

	layout = QtWidgets.QVBoxLayout(dialog)


	table = QtWidgets.QTableWidget(len(versions), 4)
	table.setHorizontalHeaderLabels(["Version", "Date", "User", "Comment"])

	for row, version in enumerate(versions):
		metadata = version["metadata"]

		version_item = QtWidgets.QTableWidgetItem(str(version["version"]))
		version_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		table.setItem(row, 0, version_item)

		date_item = QtWidgets.QTableWidgetItem(format_date(metadata.get("date", "")))
		date_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		table.setItem(row, 1, date_item)

		user_item = QtWidgets.QTableWidgetItem(metadata.get("user", ""))
		user_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		table.setItem(row, 2, user_item)

		comment_item = QtWidgets.QTableWidgetItem(metadata.get("comment", ""))
		comment_item.setToolTip(metadata.get("comment", ""))
		table.setItem(row, 3, comment_item)

	dialog.resize(700, 400)
	table.resizeColumnsToContents()
	table.resizeRowsToContents()
	table.horizontalHeader().setStretchLastSection(True)
	table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
	table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
	table.verticalHeader().setVisible(False)
	table.setTextElideMode(QtCore.Qt.TextElideMode.ElideNone)

	for col in range(table.columnCount() - 1):
		table.setColumnWidth(col, table.columnWidth(col) + 20)

	for row in range(table.rowCount()):
		table.setRowHeight(row, table.rowHeight(row) + 10)

	layout.addWidget(table)
	_history_window = dialog
	dialog.show()

def format_date(iso_text: str) -> str:
	"""Convert an ISO date to a readable date; return "" if empty."""
	if not iso_text:
		return ""
	return datetime.fromisoformat(iso_text).strftime("%d/%m/%Y\n%H:%M")