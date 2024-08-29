from qgis.core import QgsApplication, QgsCoordinateReferenceSystem
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox, QInputDialog
import geopandas as gpd
import os

def convert_kml_to_geoparquet(input_kml, output_geoparquet, crs):
    try:
        # Read the KML file into a GeoDataFrame
        gdf = gpd.read_file(input_kml, driver='KML')
        
        # Reproject the GeoDataFrame to the selected CRS
        gdf = gdf.to_crs(crs)

        # Save the GeoDataFrame to a GeoParquet file
        gdf.to_parquet(output_geoparquet, engine='pyarrow')
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
    crs, ok = QInputDialog.getText(None, "Select CRS", "Enter EPSG code (e.g., 4326 for WGS84):")

    if not ok or not crs:
        QMessageBox.warning(None, "No CRS Selected", "You need to select a CRS to continue.")
        return

    messages = []
    for kml_file in kml_files:
        # Define output file path
        base_filename = os.path.basename(kml_file)
        output_file = os.path.join(save_directory, os.path.splitext(base_filename)[0] + '.parquet')

        try:
            convert_kml_to_geoparquet(kml_file, output_file, f"EPSG:{crs}")
            messages.append(f"{kml_file} converted to {output_file}.")
        except RuntimeError as e:
            messages.append(f"Error converting {kml_file}: {str(e)}")

    # Show all messages in one window
    QMessageBox.information(None, "Conversion Results", "\n".join(messages))


main()
