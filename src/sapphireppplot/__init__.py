import paraview
import paraview.simple

# paraview.compatibility.major = 5
# paraview.compatibility.minor = 13

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
