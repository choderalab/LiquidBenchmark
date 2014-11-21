import re
from rdkit import Chem
from rdkit.Chem import AllChem
import cirpy
import pandas as pd
import glob
import thermoml_lib

data = pd.read_hdf("./data.h5", 'data')

counts_data = {}

# SEE GOOGLE DOC!!!!!!# SEE GOOGLE DOC!!!!!!# SEE GOOGLE DOC!!!!!!# SEE GOOGLE DOC!!!!!!
bad_filenames = ["./10.1016/j.fluid.2013.12.014.xml"]
data = data[~data.filename.isin(bad_filenames)]
# SEE GOOGLE DOC!!!!!!# SEE GOOGLE DOC!!!!!!# SEE GOOGLE DOC!!!!!!# SEE GOOGLE DOC!!!!!!

experiments = ["Mass density, kg/m3", "Relative permittivity at zero frequency"]  # , "Isothermal compressibility, 1/kPa", "Isobaric coefficient of expansion, 1/K"]
#experiments = ["Mass density, kg/m3"]
#experiments = ["Relative permittivity at zero frequency"]

ind_list = [data[exp].dropna().index for exp in experiments]
ind = reduce(lambda x,y: x.union(y), ind_list)
X = data.ix[ind]

counts_data["0.  Full"] = X.count()[experiments]

name_to_formula = pd.read_hdf("./compound_name_to_formula.h5", 'data')
name_to_formula = name_to_formula.dropna()


which_atoms = ["H", "N", "C", "O", "S", "Cl", "Br"]

X_is_good = {}
for k, row in X.iterrows():
    chemical_string = row.components
    chemicals = chemical_string.split("__")
    try:
        X_is_good[k] = all([thermoml_lib.is_good(name_to_formula[chemical], good_atoms=which_atoms) for chemical in chemicals])
    except KeyError:
        print("Warning, could not find %d %s" % (k, chemical_string))
        X_is_good[k] = False

X_is_good = pd.Series(X_is_good)
X["is_good"] = X_is_good
X = X[X.is_good]

X["n_components"] = X.components.apply(lambda x: len(x.split("__")))
X = X[X.n_components == 1]
X.dropna(axis=1, how='all', inplace=True)

counts_data["1.  Druglike elements"] = X.count()[experiments]

X["n_heavy_atoms"] = X.components.apply(lambda x: thermoml_lib.count_atoms(name_to_formula[x]))
X = X[X.n_heavy_atoms <= 10]
X.dropna(axis=1, how='all', inplace=True)


X["n_atoms"] = X.components.apply(lambda x: thermoml_lib.count_atoms(name_to_formula[x], which_atoms=which_atoms))
X = X[X.n_atoms <= 100]
X.dropna(axis=1, how='all', inplace=True)


counts_data["2.  10 heavy atoms, 100 atoms"] = X.count()[experiments]


X["smiles"] = X.components.apply(lambda x: cirpy.resolve(x, "smiles"))  # This should be cached via sklearn.
X = X[X.smiles != None]
X = X.ix[X.smiles.dropna().index]
    
X["cas"] = X.components.apply(lambda x: thermoml_lib.get_first_entry(cirpy.resolve(x, "cas")))  # This should be cached via sklearn.
X = X[X.cas != None]
X = X.ix[X.cas.dropna().index]



X = X[X["Temperature, K"] > 270]
X = X[X["Temperature, K"] < 330]

counts_data["3.  Temperature"] = X.count()[experiments]

X = X[X["Pressure, kPa"] > 100.]
X = X[X["Pressure, kPa"] < 102.]

counts_data["4.  Pressure"] = X.count()[experiments]

X.dropna(axis=1, how='all', inplace=True)

X["Pressure, kPa"] = 101.325  # Assume everything within range is comparable.  


mu = X.groupby(["components", "smiles", "cas", "Temperature, K", "Pressure, kPa"])[experiments].mean()
sigma = X.groupby(["components", "smiles", "cas", "Temperature, K", "Pressure, kPa"])[experiments].std().dropna()

counts_data["5.  Aggregate T, P"] = mu.count()[experiments]

counts_data = pd.DataFrame(counts_data).T

print counts_data.to_latex()

plt.figure()
X["Temperature, K"].hist()
plt.title("ThermoML Density Data")
plt.ylabel("Number of Measurements")
plt.xlabel("Temperature [K]")

plt.savefig("/home/kyleb/src/kyleabeauchamp/LiquidBenchmark/manuscript/figures/thermoml_density_histogram.pdf", bbox_inches=None)
