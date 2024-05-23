# Among-Us-read-Player
## Undetectable among us Cheat!
![x.PNG](x.PNG)


# Here's how I did it!
Use Cheat Engine
1.Link "Among Us.exe" <br>
2.Click on Mono in the toolbar up top -> Activate Mono Features
Click on dissect mono - now you will see all the dll modules in the among us game
Pick Assymbly-CSharp.dll
3.right click AmongUsClient and click on Find instances of class
4.(again) rightclick AmongUsClient and click on data structures -> Dissect Data Structue
You will see all the data structure instanses pop up, only one of them is the real one (it's better to be in a game)
5.To find the correct data structure, expand them one by one and look at the timer (right values are 0/0.013/0.033/0.066/0.099) anything that has E-XX at the end of the number is wrong (too small)
Once you find that correct data structure, you want to copy it's address into the dissect struct that you've opened before
That structure should have all game data! you can find player names/roles/XY location and other stuff there.
6.Now that we found one instance of that class, we need to find the correct pointer, for the current game version it's "GameAssembly.dll"+5C but I'll explain how to get it if the game get updated.
7.Copy the class address into Cheat Engine table, then find the pointers, once you find and save your pointers redo the whole process till you have a smaller set of pointers and pick one of them to work with it.
8.Now we found the correct pointer! WOO HOO!
Time to create our cheat!
Most anti cheats now look for a process that is linked to the among us game, or you'll get checked if you have an injected DLL in the among us folder, we DONT want that. That's how you get caught.
Instead, we will just read the data we want from the memory and display it!
I'll add the python code here for reference.
