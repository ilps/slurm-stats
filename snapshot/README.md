# Slurm GPU Snapshot
Create snapshot of GPU usage. Prepare visualizations.

# Pre-Requisites

* create a python env with python 3.9+
* install requirements in this env `pip install -r requirements.txt`

# Usage

* run `python snapshot.py` will create a CSV file `YYYYMMDDHHMMSS.csv`
* run it multiple times, collect all CSV in a `tgz` file: `tar cvzf slurm_snaphots.tgz *.csv`

* launch a jupyter lab server from your python env
* open the notebook `snapshot_viz.ipynb`
* adjust the path to the TGZ file
* run all cells to get all plots
* the plot is saved in a HTML file