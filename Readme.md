# USD morph

- To activate python from the `.venv` use `.venv/scripts/activate`
- From a DOS prompt use `.venv\scripts\activate`
- to change the version of python in that `.venv` 


# Test Command Lines
- python main.py -ifname sceneFile.usd
- python main.py --ifname USD/SceneFile.usda --ofname out/SceneFile.out.usda


# To do
- Modify meshs that are subordinate to a SkelRoot to have a 
        def Mesh "l_L_eye"( prepend apiSchemas = ["SkelBindingAPI"] )   
        
- In meshes that have an st change:
           float2[] primvars:st = [(0.5389985, 0.9019369), ... (0.49300203, 0.96518755)] (
                elementSize = 1
                interpolation = "constant"
            )
  To 
                interpolation = "varying"
  