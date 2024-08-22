import geopandas as gpd
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pyarrow as pa
import pyarrow.parquet as pq

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

    # Find all shapefiles in the input directory and subdirectories
    shapefiles = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.shp'):
                shapefiles.append(os.path.join(root, file))
    
    if not shapefiles:
        QMessageBox.warning(None, "No Shapefiles Found", "No shapefiles found in the selected directory.")
        return

    # Process each shapefile
    for shapefile_path in shapefiles:
        base_name = os.path.splitext(os.path.basename(shapefile_path))[0]
        output_file = os.path.join(output_dir, base_name + ".parquet")

        try:
            # Read the shapefile into a GeoDataFrame
            gdf = gpd.read_file(shapefile_path)

            # Write the GeoDataFrame to a GeoParquet file
            gdf.to_parquet(output_file, engine='pyarrow')

            QMessageBox.information(None, "Success", f"Shapefile successfully converted to GeoParquet: {output_file}")
        except Exception as e:
            QMessageBox.critical(None, f"Error with {shapefile_path}", f"Failed to convert shapefile to GeoParquet: {str(e)}")
            continue

# Run the function
convert_all_shapefiles_to_geoparquet()
