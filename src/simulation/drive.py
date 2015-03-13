from simtk import unit as u
import liquid_tools

builder = liquid_tools.AmberMixtureSystem(["CCO"], [1000], 300 * u.kelvin)
builder.build_amber_files()
builder.equilibrate()