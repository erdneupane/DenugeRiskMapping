#This code is used for rasterization of dengue cases
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.features import rasterize
import os

# -----------------------------
# 1. FILE PATHS
# -----------------------------
dengue_csv = r"C:\Users\dhrub\Desktop\Dengue_Ward_Monthly_Aggregated.csv"
wards_path = r"C:\Users\dhrub\Desktop\Dhurba\kaski all wardwise\all_wards.shp"
ref_raster = r"C:\Users\dhrub\Desktop\stacked indices\stacked_2019_01.tif"
output_folder = r"C:\Users\dhrub\Desktop\dengue_raster"

os.makedirs(output_folder, exist_ok=True)

# -----------------------------
# 2. LOAD DATA
# -----------------------------
wards = gpd.read_file(wards_path)
dengue = pd.read_csv(dengue_csv)

wards["ward_id"] = wards["name"].str.strip()
dengue["ward_id"] = dengue["name"].str.strip()

# -----------------------------
# 3. PROJECT WARDS TO MATCH REFERENCE CRS
# -----------------------------
with rasterio.open(ref_raster) as ref:
    ref_meta = ref.meta.copy()
    ref_crs = ref_meta["crs"]
    ref_transform = ref_meta["transform"]
    ref_width = ref_meta["width"]
    ref_height = ref_meta["height"]

# Reproject wards if needed
if wards.crs != ref_crs:
    wards = wards.to_crs(ref_crs)

print("Reference metadata loaded:")
print(ref_meta)

# -----------------------------
# 4. LOOP THROUGH YEARS & MONTHS
# -----------------------------
for YEAR in range(2019, 2026):   # 2019–2025
    for MONTH in range(1, 13):  # 1–12

        df = dengue[(dengue["year"] == YEAR) & (dengue["month"] == MONTH)]
        if df.empty:
            print(f"Skipping {YEAR}-{MONTH:02d} — no data")
            continue

        # Merge
        merged = wards.merge(df[["ward_id", "dengue_cases"]], on="ward_id", how="left")
        merged["dengue_cases"] = merged["dengue_cases"].fillna(0)

        # Prepare shapes
        shapes = list(zip(merged.geometry, merged["dengue_cases"]))

        # Rasterize using EXACT reference grid
        raster = rasterize(
            shapes=shapes,
            out_shape=(ref_height, ref_width),
            transform=ref_transform,
            fill=0,
            dtype="float32"
        )

        out_file = os.path.join(output_folder, f"dengue_{YEAR}_{MONTH:02d}.tif")

        # Save using EXACT reference metadata
        out_meta = ref_meta.copy()
        out_meta.update(count=1, dtype="float32")

        with rasterio.open(out_file, "w", **out_meta) as dst:
            dst.write(raster, 1)

        print(f"Saved aligned raster → {out_file}")

print("✔ All dengue rasters were forced to match the reference TIFF grid.")
