import os
from qgis.PyQt.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QApplication
from qgis.core import (
    QgsApplication, QgsCoordinateReferenceSystem, QgsVectorLayer,
    QgsVectorFileWriter, QgsProject, QgsDataSourceUri
)
from psycopg2 import connect, sql
import threading
import tempfile
import time

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database and Export Parameters")

        # Create form layout
        self.layout = QFormLayout(self)

        # Add input fields to the layout
        self.dbname_input = QLineEdit(self)
        self.user_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.host_input = QLineEdit(self)
        self.port_input = QLineEdit(self)
        self.schema_name_input = QLineEdit(self)
        self.output_directory_input = QLineEdit(self)
        self.crs_input = QLineEdit(self)  # New input for CRS
        self.browse_button = QPushButton("Browse", self)

        self.layout.addRow("Database Name:", self.dbname_input)
        self.layout.addRow("Database User:", self.user_input)
        self.layout.addRow("Database Password:", self.password_input)
        self.layout.addRow("Database Host:", self.host_input)
        self.layout.addRow("Database Port:", self.port_input)
        self.layout.addRow("Schema Name:", self.schema_name_input)
        self.layout.addRow("Output Directory:", self.output_directory_input)
        self.layout.addWidget(self.browse_button)
        self.layout.addRow("CRS (e.g., EPSG:4326):", self.crs_input)  # Label for CRS input

        # Add OK and Cancel buttons
        self.button_box = QVBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.button_box.addWidget(self.ok_button)
        self.button_box.addWidget(self.cancel_button)
        self.layout.addRow(self.button_box)

        # Connect signals and slots
        self.browse_button.clicked.connect(self.browse_directory)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_directory_input.setText(directory)

    def get_values(self):
        return {
            'dbname': self.dbname_input.text(),
            'user': self.user_input.text(),
            'password': self.password_input.text(),
            'host': self.host_input.text(),
            'port': self.port_input.text(),
            'schema_name': self.schema_name_input.text(),
            'output_directory': self.output_directory_input.text(),
            'crs': self.crs_input.text()  # Include CRS in returned values
        }

# Function to get all tables in the schema
def get_tables_in_schema(db_params, schema):
    try:
        conn = connect(**db_params)
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT table_name FROM information_schema.tables WHERE table_schema = %s"), [schema])
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

# Function to export each layer to GeoParquet using QGIS built-in functions
def export_to_geoparquet(db_params, schema, table, output_dir, crs):
    try:
        # Set up the connection URI
        uri = QgsDataSourceUri()
        uri.setConnection(db_params['host'], db_params['port'], db_params['dbname'], db_params['user'], db_params['password'])
        uri.setDataSource(schema, table, "geom")

        # Load the table as a QgsVectorLayer
        layer = QgsVectorLayer(uri.uri(False), table, "postgres")
        if not layer.isValid():
            raise RuntimeError(f"Failed to load layer {schema}.{table} from database")

        # Reproject the layer to the desired CRS if specified
        if crs:
            target_crs = QgsCoordinateReferenceSystem(crs)
            layer.setCrs(target_crs)
        else:
            layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Define options for saving to GeoParquet
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "Parquet"

        # Define output path
        output_path = os.path.join(output_dir, f"{table}.parquet")

        # Save the layer to GeoParquet
        error = QgsVectorFileWriter.writeAsVectorFormatV2(
            layer,
            output_path,
            QgsProject.instance().transformContext(),
            options
        )
        if error[0] != QgsVectorFileWriter.NoError:
            raise RuntimeError(f"Failed to write GeoParquet: {error[1]}")
        else:
            print(f"Successfully exported {schema}.{table} to {output_path}")

        # Remove the layer and introduce a small delay to ensure file handles are released
        QgsProject.instance().removeMapLayer(layer.id())
        del layer
        time.sleep(0.5)

    except Exception as e:
        print(f"Exception during export: {e}")

def run_export(db_params, schema_name, output_directory, crs):
    # Get all tables in the schema
    tables = get_tables_in_schema(db_params, schema_name)

    # Export each table to GeoParquet
    for table in tables:
        export_to_geoparquet(db_params, schema_name, table, output_directory, crs)

# Show input dialog
dialog = InputDialog()
if dialog.exec_() == QDialog.Accepted:
    values = dialog.get_values()

    # Define your database connection parameters
    db_params = {
        'dbname': values['dbname'],
        'user': values['user'],
        'password': values['password'],
        'host': values['host'],
        'port': values['port']
    }
    schema_name = values['schema_name']
    output_directory = values['output_directory']
    crs = values['crs']

    # Run the export process in a separate thread
    export_thread = threading.Thread(target=run_export, args=(db_params, schema_name, output_directory, crs))
    export_thread.start()
else:
    print("Input dialog was canceled or invalid.")
