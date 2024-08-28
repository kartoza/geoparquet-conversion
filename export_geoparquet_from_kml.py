from qgis.core import (
    QgsApplication, QgsCoordinateReferenceSystem, QgsVectorLayer,
    QgsVectorFileWriter, QgsProject
)
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox, QInputDialog
import os

def convert_kml_to_geoparquet(input_kml, output_geoparquet, crs_epsg):
    try:
        # Load the KML file as a QGIS layer
        kml_layer = QgsVectorLayer(input_kml, "layer", "ogr")
        if not kml_layer.isValid():
            raise RuntimeError(f"Failed to load KML file: {input_kml}")

        # Set the target CRS
        crs = QgsCoordinateReferenceSystem(crs_epsg)
        kml_layer.setCrs(crs)

        # Reproject the layer to the desired CRS
        reprojected_layer = kml_layer.clone()
        reprojected_layer.setCrs(crs)

        # Save the layer to GeoParquet
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "Parquet"
        error = QgsVectorFileWriter.writeAsVectorFormatV2(
            reprojected_layer,
            output_geoparquet,
            QgsProject.instance().transformContext(),
            options
        )

        if error[0] != QgsVectorFileWriter.NoError:
            raise RuntimeError(f"Failed to write GeoParquet: {error[1]}")
    except Exception as e:
        raise RuntimeError(f"Failed to convert {input_kml} to GeoParquet: {e}")

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

    # Input dialog to select the CRS
    crs_epsg, ok = QInputDialog.getText(None, "Select CRS", "Enter EPSG code (e.g., 4326 for WGS84):")

    if not ok or not crs_epsg:
        QMessageBox.warning(None, "No CRS Selected", "You need to select a CRS to continue.")
        return

    messages = []
    for kml_file in kml_files:
        # Define output file path
        base_filename = os.path.basename(kml_file)
        output_file = os.path.join(save_directory, os.path.splitext(base_filename)[0] + '.parquet')

        try:
            convert_kml_to_geoparquet(kml_file, output_file, int(crs_epsg))
            messages.append(f"{kml_file} converted to {output_file}.")
        except RuntimeError as e:
            messages.append(f"Error converting {kml_file}: {str(e)}")

    # Show all messages in one window
    QMessageBox.information(None, "Conversion Results", "\n".join(messages))


main()

