import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QgsVectorFileWriter

def convert_all_shapefiles_to_geoparquet():
    # Open file dialog to select input directory
    input_dir = QFileDialog.getExistingDirectory(None, "Select Input Directory")
    if not input_dir:
        QMessageBox.warning(None, "No Directory Selected", "You must select an input directory.")
        return

    # Open file dialog to select output directory
    output_dir = QFileDialog.getExistingDirectory(None, "Select Output Directory")
    if not output_dir:
        QMessageBox.warning(None, "No Directory Selected", "You must select an output directory.")
        return

    # Get the desired CRS from the user
    crs, ok = QInputDialog.getText(None, "Input CRS", "Enter the EPSG code for the desired CRS (e.g., 'EPSG:4326'):")
    if not ok or not crs:
        QMessageBox.warning(None, "No CRS Selected", "You must enter a valid CRS.")
        return

    # Find all shapefiles in the input directory and subdirectories
    shapefiles = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.shp'):
                shapefiles.append(os.path.join(root, file))
    
    if not shapefiles:
        QMessageBox.warning(None, "No Shapefiles Found", "No shapefiles found in the selected directory.")
        return

    # Collect all messages to display later
    messages = []

    # Process each shapefile
    for shapefile_path in shapefiles:
        base_name = os.path.splitext(os.path.basename(shapefile_path))[0]
        output_file = os.path.join(output_dir, base_name + ".parquet")

        try:
            # Load the shapefile into a QGIS vector layer
            layer = QgsVectorLayer(shapefile_path, base_name, "ogr")
            if not layer.isValid():
                raise Exception("Failed to load layer")

            # Set the CRS
            target_crs = QgsCoordinateReferenceSystem(crs)
            layer.setCrs(target_crs)

            # Save the layer as a GeoParquet file
            QgsVectorFileWriter.writeAsVectorFormat(layer, output_file, "utf-8", target_crs, "Parquet")

            messages.append(f"Success: {shapefile_path} -> {output_file}")
        except Exception as e:
            messages.append(f"Error with {shapefile_path}: {str(e)}")
            continue

    # Display all messages in one window
    QMessageBox.information(None, "Conversion Results", "\n".join(messages))

# Run the function
convert_all_shapefiles_to_geoparquet()
