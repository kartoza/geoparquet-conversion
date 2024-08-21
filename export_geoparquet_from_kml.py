from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
import geopandas as gpd
import os

def convert_kml_to_flatgeobuf(input_kml, output_flatgeobuf):
    try:
        # Read the KML file into a GeoDataFrame
        gdf = gpd.read_file(input_kml, driver='KML')
        
        # Save the GeoDataFrame to a FlatGeobuf file
        gdf.to_file(output_flatgeobuf, driver='FlatGeobuf')
    except Exception as e:
        raise RuntimeError(f"Failed to convert {input_kml} to FlatGeobuf: {e}")

def main():
    # Open file dialog to choose KML files
    kml_files, _ = QFileDialog.getOpenFileNames(
        None, "Select KML Files", "", "KML Files (*.kml)"
    )

    if not kml_files:
        QMessageBox.warning(None, "No Files Selected", "You need to select at least one KML file.")
        return

    # Open directory dialog to choose save directory
    save_directory = QFileDialog.getExistingDirectory(
        None, "Select Save Directory"
    )

    if not save_directory:
        QMessageBox.warning(None, "No Directory Selected", "You need to select a directory to save the converted files.")
        return

    for kml_file in kml_files:
        # Define output file path
        base_filename = os.path.basename(kml_file)
        output_file = os.path.join(save_directory, os.path.splitext(base_filename)[0] + '.fgb')

        try:
            convert_kml_to_flatgeobuf(kml_file, output_file)
            QMessageBox.information(None, "Conversion Successful", f"{kml_file} converted to {output_file}.")
        except RuntimeError as e:
            QMessageBox.critical(None, "Error", str(e))

main()
