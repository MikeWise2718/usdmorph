# USD morph - 27 Dec 2021

- USD is Pixar's "Universal Scene Descriptor" format - a multi-file geometric scene specification language that can accomidate movement among other things.
- This is a python implementation of a minimal parsing program that reads in a USDA formatted files, looks for patterns that correspond to multiple known bugs in Unity's USD output package and corrects them. 

- The bugs are detailed on the Unity USD GitHub issue page: (https://github.com/Unity-Technologies/usd-unity-sdk/issues)
   - Issue 285 - (https://github.com/Unity-Technologies/usd-unity-sdk/issues/285)
   - Issue 284 - (https://github.com/Unity-Technologies/usd-unity-sdk/issues/284)
   - Issue 283 - (https://github.com/Unity-Technologies/usd-unity-sdk/issues/283)
   - Issue 282 - (https://github.com/Unity-Technologies/usd-unity-sdk/issues/282)
   - Issue 278 - (https://github.com/Unity-Technologies/usd-unity-sdk/issues/278)
- These bugs caused the objects to appear at the wrong place, surface specifiers to be ignored, the animation skinning to not work, texture maps to fail, and also produced excessive depreciation warnings. 
- The "parser" is really quite minimal and not deserving of that name, but it suffices to correct the errors that blocked me and more would have been a lot more work.

# Directories

# Install and build Instructions
- Should work by cloning 
- How to create the .venv (see VS Code docs)
- Currently using Windows 10 and C-Python 3.10.1
- This is setup for use with VS Code, if you are using anything else you are on your own
- To install packages use `python -m pip install -r requirements.txt`
   - Note that using `pip` as a standalone module might install to the wrong python 
   - To see location `pip show pip`
- (Windows) To activate python from the `.venv` use `.venv/scripts/activate`
- From a CMD prompt use `.venv\scripts\activate`


# Testing
- We are using the pytest framework
- From the root directory (the one with main.py in it) you should be able to run all tests with `python -m pytest tests`
- If you want to avoid calling pytest through python, then just make sure the root directory (or .) is in Python path
   - see `https://docs.pytest.org/en/latest/how-to/usage.html`
- If you want to run tests directly from VS code you need to configure the test directory for pytest in the Test Explorer 
   - This is found in the test flask icon in the left-vertical icons bar found with the other vs-code extensions


# To Do
* Do to do list
* Add a pytest test case
   * Directory
   * Test code
   * Test script
- Factor out morphing objects
- Document Directories
- Document Installation
   - how to create that .venv (VS Code docs)
- Add Code Coverage
- Redo logging to use standard logging module 



# Test Command Lines
Actually most bat files also contain activations
```
python main.py -ifname sceneFile.usd
python main.py --ifname USD/SceneFile.usda --ofname out/SceneFile.out.usda
```

