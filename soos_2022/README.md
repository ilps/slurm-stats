# slurm-stats
Plots and Viz from the "Slurm in 2021" presentation

# Pre-Requisites

* create a python env with python 3.9+
* install requirements in this env `pip install -r requirements.txt`

# Usage

* log in the SLURM cluster head node
* launch `bash run_sacct.sh`
* it create a file named `slurm_stats.csv`

* launch a jupyter lab server from your python env
* open the notebook `slurm_accounting.ipynb`
* adjust the path to the CSV file
* run all cells to get all plots
* each plot is saved in a PDF file