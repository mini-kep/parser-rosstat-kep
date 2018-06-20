VS CODE QUESTIONS
=================

1. Spyder style intepreter (leaves command line open after running a script)

   - In PyCharm, can edit run configuration by setting Leave command line open 
     afterwards. Ipython is also self-disovered.

   - In VS Code I can add `-i` to `"python.terminal.launchArgs": ["-i"]`,
     this will open the interpreter after module run, but I have to close the 
     interpreter each time with `Ctrl-Z + Enter`. (Note: this works in Integrated Terminal Window.)
     
   - This is not great solution because I have to close the interpreter every time 
     I need a new run: Ctrl-Z + Enter + key up + Enter to repeat 
     that is awful lot of typing compared to Spyder, where re-runs, and running parts of 
     code is much easier.

   - Alternatively in VS Code I can set a breakpoint at the end of a file and use debugger, 
     but it seems a workaround - the debugger is really for getting to inside of a program, 
     not end of it. (Note: This woks in Debugging Console Window.)
     
   - Maybe the workflow in Spyder is generally different from Pycharm and VS Code:
     Spyder is a lot like RStudio / Matlab - it has an interpreter open for you 
     to experiment and trail and see things quickly. 
     
   - It also feels like VS Code is good to work with mature codebase and tests,
     and it is not greatly suited to experiment with parts of code and writing new code 
     from scratch quiclky.     

2. Can I quickly disable specific lint errors in the IDE, not a config file? 

3. How can I find all entries of a string (variable name) in all files in a  project?

   Shift-F12 seems to look in one file only. 

4. Can I see code coverage in VS Code?  

5. Rename a module in a package and change its all dependencies. 

6. For <project/src/my_package/subpackage/module_a> structure I had to change %PYTHONPATH% manually 
   to <project/src> to make `import my_package.subpackage.module_a` work. Also relative imports do 
   not work. 
   
7. Why not save files before running a test? There should be an option for that.

8. Extenstion 'Runner' had a button to run, 'Python' extenstion only has a mouse-menu item. 
   Should runner still be used?

9. Run files with relative imports - getting an error:

```
 
  File "C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/kep/csv2df/tests/test_reader.py", line 5, in <module>
    from ..reader import get_year, is_year, Row

  ValueError: attempted relative import beyond top-level package
 
```