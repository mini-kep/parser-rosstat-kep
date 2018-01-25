VS CODE QUESTIONS
=================

1. Spyder style intepreter (leaves command line open after running a script)

   - In PyCharm, can edit run configuration by setting Open 

   - In VS Code I can add `-i` to `"python.terminal.launchArgs": ["-i"]`,
     this will open the interpreter after module run, but I have to close the 
     interpreter each time with `Ctrl-Z + Enter`. This works in Integrated Terminal Window.

   - Alternatively I can set a breakpoint at the end of a file and use debugger, but
     it seems a workaround - the debugger is really for getting to inside of a program, 
     not end of it. This woks is Debugging Console Window.    

2. Can I quickly disable specific lint errors in the IDE, not a config file? 

3. How can I find all entries of a string (variable name) in all files in a 
   project?

   Shift-F12 seems to look in one file only. 

4. Can I see code coverage in VS Code?  

5. Rename a module in a package and change its all dependencies. 
   
   

     