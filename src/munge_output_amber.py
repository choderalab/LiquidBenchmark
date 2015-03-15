import chemistry
from gaff2xml import cirpy
import mdtraj as md
import pymbar
import os
import pandas as pd
import glob
import dipole_errorbars

PATH = "./liquid_benchmark_3_14/"

num_bootstrap = 100
fixed_block_length = 20  # 200 ps blocks for dielectric error bar block averaging.

prmtop_filenames = glob.glob(PATH + "/tleap/*.prmtop")
filename_munger = lambda filename: os.path.splitext(os.path.split(filename)[1])[0].split("_")
data = []
for prmtop_filename in prmtop_filenames[0:2]:
    cas, n_molecules, temperature = filename_munger(prmtop_filename)
    print(cas, temperature)
    dcd_filename = PATH + "/production/%s_%s_%s_production.dcd" % (cas, n_molecules, temperature)
    csv_filename = PATH + "/production/%s_%s_%s_production.csv" % (cas, n_molecules, temperature)
    try:
        traj = md.load(dcd_filename, top=prmtop_filename)
    except IOError:
        continue
    if traj.unitcell_lengths is None: continue
    rho = pd.read_csv(csv_filename)["Density (g/mL)"].values * 1000.  # g / mL -> kg /m3
    [t0, g, Neff] = pymbar.timeseries.detectEquilibration(rho)
    mu = rho[t0:].mean()
    sigma = rho[t0:].std() * Neff ** -0.5
    prmtop = chemistry.load_file(prmtop_filename)
    charges = prmtop.to_dataframe().charge.values
    temperature = float(temperature)
    traj = traj[t0 * len(traj) / len(rho):]
    dielectric = md.geometry.static_dielectric(traj, charges, temperature)
    dielectric_sigma_fixedblock = dipole_errorbars.bootstrap_old(traj, charges, temperature, fixed_block_length)[1]
    block_length = dipole_errorbars.find_block_size(traj, charges, temperature)
    dielectric_sigma = dipole_errorbars.bootstrap(traj, charges, temperature, block_length, num_bootstrap)
    formula = cirpy.resolve(cas, "formula")
    data.append(dict(cas=cas, temperature=temperature, density=mu, density_sigma=sigma, Neff=Neff, n_frames=traj.n_frames, dielectric=dielectric, dielectric_sigma=dielectric_sigma, dielectric_sigma_fixedblock=dielectric_sigma_fixedblock, block_length=block_length, formula=formula))
    print(data[-1])

data = pd.DataFrame(data)

data.to_csv("./tables/predictions.csv")