# This code is used for stacking the dengue cases raster with indices derived from GEE (LSTd, LSTn, Precipatation, NDVI, EVI)
import rasterio
import numpy as np
import os

# --------------------------------------
# USER INPUTS
# --------------------------------------

input_dir = r"C:\Users\dhrub\Desktop\dengue_raster"
output_dir = r"C:\Users\dhrub\Desktop\STACKED_RASTERS"

os.makedirs(output_dir, exist_ok=True)

for year in range(2019, 2026):
    for month in range(1, 13):

        dengue_file = os.path.join(input_dir, f"dengue_{year}_{month:02d}.tif")
        indices_file = os.path.join(input_dir, f"stacked_{year}_{month:02d}.tif")
        output_file = os.path.join(output_dir, f"stack_{year}_{month:02d}.tif")

        if not (os.path.exists(dengue_file) and os.path.exists(indices_file)):
            print(f"Skipping {year}-{month:02d}: missing file")
            continue

        with rasterio.open(dengue_file) as src1:
            dengue_data = src1.read()
            profile = src1.profile

        with rasterio.open(indices_file) as src2:
            indices_data = src2.read()

        if dengue_data.shape[1:] != indices_data.shape[1:]:
            print(f"ERROR: Size mismatch at {year}-{month:02d}")
            continue

        stacked = np.vstack([dengue_data, indices_data])

        profile.update(count=stacked.shape[0])

        band_names = [
            "Dengue",
            "NDVI",
            "EVI",
            "LST_DAY",
            "LST_NIGHT",
            "PRECIPITATION"
        ]

        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(stacked)

            # For QGIS/ArcGIS band names
            for i, name in enumerate(band_names, start=1):
                dst.set_band_description(i, name)

            # Save metadata tag
            dst.update_tags(band_names=",".join(band_names))

        print(f"Saved: {output_file}")
