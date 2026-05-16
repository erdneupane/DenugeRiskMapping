import rasterio
import numpy as np
import pandas as pd
import glob
import os

# Folder containing your final stacked rasters
folder = r"C:\Users\dhrub\Desktop\STACKED_RASTER"

# Output CSV
out_csv = r"C:\Users\dhrub\Desktop\Dengue_summary_report\ML_training_data.csv"

all_data = []

# Loop through all stacked TIFFs (sorted by name)
for file in sorted(glob.glob(os.path.join(folder, "*.tif"))):

    print("Processing:", file)

    # Extract year and month from filename
    # Example filename: stack_2019_01.tif
    base = os.path.basename(file)
    parts = base.replace(".tif", "").split("_")
    year = int(parts[-2])
    month = int(parts[-1])

    # Read raster stack
    with rasterio.open(file) as src:
        bands = []
        for i in range(1, src.count + 1):
            band = src.read(i).astype(float).flatten()
            bands.append(band)

    # Stack bands → shape (pixels, features)
    arr = np.vstack(bands).T

    # Remove pixels with NoData
    arr = arr[~np.any(np.isnan(arr), axis=1)]

    # Create DataFrame
    df = pd.DataFrame(arr, columns=[f"band_{i}" for i in range(1, src.count + 1)])

    # Add metadata
    df["year"] = year
    df["month"] = month

    all_data.append(df)

# Combine all months
final_df = pd.concat(all_data, ignore_index=True)

# Save CSV
final_df.to_csv(out_csv, index=False)

print("DONE! Saved:", out_csv)
