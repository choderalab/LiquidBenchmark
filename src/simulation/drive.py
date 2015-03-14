from simtk import unit as u
import liquid_tools

builder = liquid_tools.AmberMixtureSystem(["CO"], [1000], 300 * u.kelvin)
builder.run()
