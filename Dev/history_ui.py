from pathlib import Path

import hou
import hdefereval

from houdini_tools import version_up
from PySide6 import QtWidgets, QtCore
from datetime import datetime

from core import (parse_scene_name, build_scene_folder, list_versions)


def create_history_panel():
	"""Build the history widget for a Houdini Python Panel."""
	widget = QtWidgets.QWidget()
	layout = QtWidgets.QVBoxLayout(widget)

	title = QtWidgets.QLabel()
	table = QtWidgets.QTableWidget(0, 4)
	table.setHorizontalHeaderLabels(["Version", "Date", "User", "Comment"])

	table.setTextElideMode(QtCore.Qt.TextElideMode.ElideNone)

	table.verticalHeader().setVisible(False)
	table.horizontalHeader().setStretchLastSection(True)

	table.setAlternatingRowColors(True)
	table.setShowGrid(False)
	table.setStyleSheet("""
		QTableWidget {
			font-size: 12px;
		}
		QTableWidget::item {
			padding: 6px;
		}
		QTableWidget::item:selected {
			background-color: #2f7f86;
			color: white;
		}
		QHeaderView::section {
			background-color: #1e1e1e;
			color: #4fc3c9;
			font-weight: bold;
			padding: 4px;
		}
	""")

	versions = []

	def on_scene_event(event_type):
		if event_type in (
			hou.hipFileEventType.AfterSave,
			hou.hipFileEventType.AfterLoad,
			hou.hipFileEventType.AfterClear,
		):
			refresh()

	hou.hipFile.addEventCallback(on_scene_event)
	widget.destroyed.connect(lambda: hou.hipFile.removeEventCallback(on_scene_event))

	def refresh():
		nonlocal versions
		scene_name = hou.hipFile.basename()
		name_parse = parse_scene_name(scene_name)
		if name_parse is None:
			title.setText("Scene not versioned")
			table.setRowCount(0)
			return
		shot, task, _= name_parse
		job =hou.getenv("JOB")
		if job is None:
			title.setText("$JOB not defined")
			table.setRowCount(0)
			return
		scene_folder = build_scene_folder(Path(job), shot, task)
		versions = list_versions(scene_folder, shot, task)
		title.setText(f"{shot} / {task}")
		table.setRowCount(len(versions))

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

			table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
			table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
			table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

		table.resizeColumnsToContents()
		table.resizeRowsToContents()


	def open_selected():
		row = table.currentRow()
		if row == -1:
			hou.ui.displayMessage("Select a version first.")
			return
		path = versions[row]["path"]
		hdefereval.executeDeferred(lambda: open_version(path))

	refresh_button = QtWidgets.QPushButton("Refresh")
	refresh_button.clicked.connect(refresh)
	open_button = QtWidgets.QPushButton("Open version")
	open_button.clicked.connect(open_selected)
	table.cellDoubleClicked.connect(lambda row, col: open_selected())

	layout.addWidget(title)
	layout.addWidget(table)
	layout.addWidget(refresh_button)
	layout.addWidget(open_button)

	refresh()
	return widget

def format_date(iso_text: str) -> str:
	"""Convert an ISO date to a readable date; return "" if empty."""
	if not iso_text:
		return ""
	return datetime.fromisoformat(iso_text).strftime("%d/%m/%Y\n%H:%M")

def open_version(path):
	"""Ask about unsaved changes, then load the given scene."""
	if hou.hipFile.hasUnsavedChanges():
		ask = hou.ui.displayMessage(
			"The current scene has unsaved changes.",
			buttons=("Version up", "Open without save", "Cancel"),
			close_choice=2,
		)
		if ask == 2:
			return
		elif ask == 0:
			if not version_up():
				return
	hou.hipFile.load(str(path), suppress_save_prompt=True, ignore_load_warnings=True)