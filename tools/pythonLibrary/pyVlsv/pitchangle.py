from vlsvreader import *
import numpy as np
import pylab as pl

def get_pitch_angles( fileName, cellid, bins=100, cosine=True, log=False, plasmaframe=False ):
   # Open the file
   vlsvReader = VlsvFile( fileName )
   # Read the velocity cells:
   print "Reading.."
   velocity_cell_data = vlsvReader.read_velocity_cells(cellid)
   # Read bulk velocity:
   bulk_velocity = np.array(vlsvReader.read_variable("rho_v", cellid) / vlsvReader.read_variable("rho", cellid))
   print bulk_velocity
   print "Calculating.."
   # Calculate the pitch angles for the data:
   B = vlsvReader.read_variable("B", cellid)
   B_unit = B / np.linalg.norm(B)
   # Get cells:
   vcellids = velocity_cell_data.keys()
   # Get avgs data:
   avgs = velocity_cell_data.values()
   # Get a list of velocity coordinates:
   if plasmaframe == True:
      v = vlsvReader.get_velocity_cell_coordinates(vcellids) / bulk_velocity
   else:
      v = vlsvReader.get_velocity_cell_coordinates(vcellids)
   # Get norms:
   v_norms = np.sum(np.abs(v)**2,axis=-1)**(1./2)
   # Get the angles:
   if cosine == True:
      pitch_angles = v.dot(B_unit) / v_norms
   else:
      pitch_angles = np.arccos(v.dot(B_unit) / v_norms) / (2*np.pi) * 360
   # Plot the pitch angles:
   pl.hist(pitch_angles, weights=avgs, bins=bins, log=log)
   #pl.xlim=([0,180])
   #pl.show()


