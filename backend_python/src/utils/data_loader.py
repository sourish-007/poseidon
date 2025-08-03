import xarray as xr

def load_dataset(file_path):
    return xr.open_dataset(file_path)