"""sapphireppplot package: A ParaView Python package to plot the results from Sapphire++."""

import paraview
import paraview.simple

# paraview.compatibility.major = 6
# paraview.compatibility.minor = 0

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
