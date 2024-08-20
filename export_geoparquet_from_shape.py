import geopandas as gpd
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox

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

    # List all shapefiles in the input directory
    shapefiles = [f for f in os.listdir(input_dir) if f.lower().endswith('.shp')]
    if not shapefiles:
        QMessageBox.warning(None, "No Shapefiles Found", "No shapefiles found in the selected directory.")
        return

    # Process each shapefile
    for shapefile in shapefiles:
        shapefile_path = os.path.join(input_dir, shapefile)
        base_name = os.path.splitext(shapefile)[0]
        output_file = os.path.join(output_dir, base_name + ".parquet")

        try:
            # Read the shapefile into a GeoDataFrame
            gdf = gpd.read_file(shapefile_path)

            # Write the GeoDataFrame to a GeoParquet file
            gdf.to_parquet(output_file)

            QMessageBox.information(None, "Success", f"Shapefile successfully converted to GeoParquet: {output_file}")
        except Exception as e:
            QMessageBox.critical(None, f"Error with {shapefile}", f"Failed to convert shapefile to GeoParquet: {str(e)}")
            continue

# Run the function
convert_all_shapefiles_to_geoparquet()
