#!/usr/bin/env python3
"""
Textual Plugin Viewer - Browse and search your plugin collection
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, Header, Input, Static
from textual.binding import Binding


class PluginViewer(App):
   """A Textual app to view plugin data with search and sort."""

   CSS = """
    Screen {
        background: $surface;
    }

    #search-container {
        height: 3;
        margin: 1 1 0 1;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    #search-input {
        width: 100%;
    }

    #stats {
        height: 2;
        margin: 0 1;
        color: $text-muted;
        text-align: right;
    }

    #table-container {
        margin: 1;
        height: 1fr;
        border: solid $primary;
    }

    DataTable {
        width: 100%;
        height: 100%;
    }
    """

   BINDINGS = [
      Binding("q", "quit", "Quit"),
      Binding("/", "focus_search", "Search"),
      Binding("r", "clear_search", "Clear Search"),
   ]

   def __init__(self):
      super().__init__()
      self.plugins: List[Dict] = []
      self.filtered_plugins: List[Dict] = []
      self.sort_key: str = "name"
      self.sort_reverse: bool = False
      self.search_query: str = ""

   def compose(self) -> ComposeResult:
      """Create the layout."""
      yield Header()

      with Container(id="search-container"):
         yield Input(
            placeholder="Search plugins... (Name, Manufacturer, Description)",
            id="search-input",
         )

      with Vertical(id="stats-container"):
         yield Static("Showing 0 of 0 plugins", id="stats")

      with Container(id="table-container"):
         yield DataTable(id="plugins-table")

      yield Footer()

   def on_mount(self) -> None:
      """Load data and set up the table."""
      self.load_data()
      self.setup_table()
      self.populate_table()

   def load_data(self) -> None:
      """Load plugins from JSON file."""
      plugins_path = Path(__file__).parent / "Plugins.json"
      try:
         with open(plugins_path, "r") as f:
            self.plugins = json.load(f)
         self.filtered_plugins = self.plugins.copy()
         self.title = f"Plugin Viewer - {len(self.plugins)} plugins"
      except Exception as e:
         self.plugins = []
         self.filtered_plugins = []
         self.title = f"Plugin Viewer - Error loading data"
         self.notify(f"Error loading plugins: {e}", severity="error")

   def setup_table(self) -> None:
      """Configure the data table columns."""
      table = self.query_one("#plugins-table", DataTable)

      columns = [
         ("Plugin Type", "type"),
         ("Name", "name"),
         ("Manufacturer", "manufacturer"),
         ("Description", "description"),
         ("Investigate", "investigate"),
      ]

      for label, key in columns:
         table.add_column(label, key=key, width=20)

      table.zebra_stripes = True
      table.cursor_type = "row"

      table.focus()

   def populate_table(self) -> None:
      """Fill the table with plugin data."""
      table = self.query_one("#plugins-table", DataTable)
      table.clear()

      for plugin in self.filtered_plugins:
         table.add_row(
            plugin.get("Plugin Type", ""),
            plugin.get("Name", ""),
            plugin.get("Manufacturer", ""),
            plugin.get("Description", ""),
            plugin.get("Invsestigate", ""),
         )

      total = len(self.plugins)
      shown = len(self.filtered_plugins)
      self.query_one("#stats", Static).update(f"Showing {shown} of {total} plugins")

   def filter_plugins(self, query: str) -> None:
      """Filter plugins based on search query."""
      self.search_query = query

      if not query.strip():
         self.filtered_plugins = self.plugins.copy()
      else:
         query_lower = query.lower()
         self.filtered_plugins = []

         for plugin in self.plugins:
            searchable_text = " ".join(
               [
                  plugin.get("Name", ""),
                  plugin.get("Manufacturer", ""),
                  plugin.get("Description", ""),
                  plugin.get("Plugin Type", ""),
                  plugin.get("Invsestigate", ""),
               ]
            ).lower()

            if query_lower in searchable_text:
               self.filtered_plugins.append(plugin)

      self.sort_plugins()

   def sort_plugins(self) -> None:
      """Sort the plugins based on current sort settings."""
      if not self.filtered_plugins:
         return

      def get_sort_value(plugin: Dict) -> str:
         key_map = {
            "type": "Plugin Type",
            "name": "Name",
            "manufacturer": "Manufacturer",
            "description": "Description",
            "investigate": "Invsestigate",
         }

         field = key_map.get(self.sort_key, "Name")
         value = plugin.get(field, "")
         return str(value).lower()

      self.filtered_plugins.sort(key=get_sort_value, reverse=self.sort_reverse)

      if self.sort_reverse:
         self.filtered_plugins.reverse()

      self.populate_table()

   def on_data_table_column_selected(self, event: DataTable.ColumnSelected) -> None:
      """Handle column header clicks for sorting."""
      column_key = event.column_key

      key_map = {
         "type": "Plugin Type",
         "name": "Name",
         "manufacturer": "Manufacturer",
         "description": "Description",
         "investigate": "Invsestigate",
      }

      column_name = key_map.get(column_key, "Name")

      if self.sort_key == column_name.lower().replace(" ", ""):
         self.sort_reverse = not self.sort_reverse
      else:
         self.sort_key = column_name.lower().replace(" ", "")
         self.sort_reverse = False

      self.sort_plugins()

   def on_input_submitted(self, event: Input.Submitted) -> None:
      """Handle search input submission."""
      if event.input.id == "search-input":
         self.filter_plugins(event.value)

   def on_input_changed(self, event: Input.Changed) -> None:
      """Handle live search as user types."""
      if event.input.id == "search-input":
         self.filter_plugins(event.value)

   def action_focus_search(self) -> None:
      """Focus the search input."""
      self.query_one("#search-input", Input).focus()

   def action_clear_search(self) -> None:
      """Clear the search and show all plugins."""
      search_input = self.query_one("#search-input", Input)
      search_input.value = ""
      self.filtered_plugins = self.plugins.copy()
      self.sort_plugins()


if __name__ == "__main__":
   app = PluginViewer()
   app.run()
