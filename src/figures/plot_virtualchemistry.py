import statsmodels.formula.api as sm
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import simtk.unit as u
import polarizability

sns.set_palette("bright")
sns.set_style("whitegrid")

metadata = pd.read_table("./virtualchemistry.tab").set_index("cas")

data = pd.read_csv("./vchem.csv").set_index("cas")
data["density"]["646-06-0"] = 1060.  # http://en.wikipedia.org/wiki/Dioxolane

data["formula"] = metadata.formula
data["polcorr"] = pd.Series(dict((cas, polarizability.dielectric_correction_from_formula(formula, density * u.grams / u.milliliter)) for cas, (formula, density) in data[["formula", "density"]].iterrows()))

data["gaff_corrected"] = data.gaff + data.polcorr
data["opls_corrected"] = data.opls + data.polcorr


figure()
x, y = data["gaff"], data["expt"]
ols_model = sm.OLS(y, x)
ols_results = ols_model.fit()
r2 = ols_results.rsquared
#plot(x, y, 'o', label="GAFF (R^2 = %.3f)" % r2)
plot(x ** -1, y ** -1, 'o', label="GAFF")

x, y = data["gaff_corrected"], data["expt"]
ols_model = sm.OLS(y, x)
ols_results = ols_model.fit()
r2 = ols_results.rsquared
#plot(x, y, 'o', label="Corrected (R^2 = %.3f)" % r2)
plot(x ** -1, y ** -1, 'o', label="Corrected")


plt.plot([0.01, 1], [0.01, 1], 'k')  # Guide
xlim((0.01, 1))
ylim((0.01, 1))


xlabel("Predicted")
ylabel("Experiment")
title("Inverse Static Dielectric (Virtual Chemistry Data; GAFF)")

legend(loc=0)

savefig("./manuscript/figures/dielectric_virtual_chemistry_gaff.pdf", bbox_inches=None)


figure()
x, y = data["opls"], data["expt"]
ols_model = sm.OLS(y, x)
ols_results = ols_model.fit()
r2 = ols_results.rsquared
#plot(x, y, 'o', label="OPLS (R^2 = %.3f)" % r2)
plot(x ** -1, y ** -1, 'o', label="OPLS")

x, y = data["opls_corrected"], data["expt"]
ols_model = sm.OLS(y, x)
ols_results = ols_model.fit()
r2 = ols_results.rsquared
#plot(x, y, 'o', label="Corrected (R^2 = %.3f)" % r2)
plot(x ** -1, y ** -1, 'o', label="Corrected")


plt.plot([0.01, 1], [0.01, 1], 'k')  # Guide
xlim((0.01, 1))
ylim((0.01, 1))


xlabel("Predicted")
ylabel("Experiment")
title("Inverse Static Dielectric (Virtual Chemistry Data; OPLS)")

legend(loc=0)

savefig("./manuscript/figures/dielectric_virtual_chemistry_opls.pdf", bbox_inches=None)

