# Lazor
This is a project for Software Carpentry, Spring 2019.<br>
The goal of this project is to build up a code that will automatically find solutions to the “Lazor” game on phones.<br>
You could share the project
## How to use
* The only thing that need to change is the the path for the folder that contain all the .bff file.<br>
* Use python 3.7 to run the code.
* The code is run paralleling.
* If you only want the code run paralleling then run the `project.py`
* If you want to gain an extra boost for the multiprocessing code then you can try the cython folder.
* for the uncompiled_cython folder:
  > first run the following code to compiled the python code to C++
  ```
  python setup.py build_ext --inplace
  ```
  >if compiled successfully, then run the following code to start the solving.
  ```
  python run_this.py
  ```
## Highlights
* The folder don't need to be a exclusive folder for the bff file. The folder can have different kind of file in it and the code can run properly.<br>
* The out file is automatically generated and put into the same folder with all the input bff file.<br>
* The code can run super fast. It only take `65.23 seconds` to `solve all 8 level` and output to a file.
* I use multiprocessing to speed up the solving process. The code can take up the full capacity of your CPU.
* If you want to gain an extra boost for the code. Then you could try the codes in the uncompiled_cython folder. It will compile the python code to C package and gain an extra speed up.
* After the compile the run time for the code can reach `58.24 seconds` to `solve all 8 level`.         
## Benchmark
The detail information for the multiprocessing test run:<br>
   
                          OS:                            Win 10
                          Python version:                3.7
                          CPU:                           Intel Core i5-8300H
                          memory:                        8 GB
                          number of files for one test:  8 files
                          total run time(seconds):       65.23 s
The detail information for the boost after compiled to C package:<br>
   
                          OS:                            Win 10
                          Python version:                3.7
                          CPU:                           Intel Core i5-8300H
                          memory:                        8 GB
                          number of files for one test:  8 files
                          total run time(seconds):       58.24 s
                          


## Notice
* The input file must be .bff file.
* To improve the speed, I have to trade memory for speed. There isn't any memory overflow problem for the test run and the test file. But if there is a level with huge amount of combination to place the blocks there might be a potential memory overflow problem.
* When you use windows there may encounter a error when compile to C++, this is probably because you don't got a C++ compiler. Just dowenload the latest Visual Studio build tools.
* In the output file:<br>
  > o: vacant position<br>
  > x: no block allowed position<br>
  > A: reflect block<br>
  > B: opaque block<br>
  > C: refract block<br>
* This code apply for Lazor boards with reflect, refract, and opaque blocks only. It does not include solutions with black hole blocks(which teleport the laser from one block to another) and diamond blocks(the laser enter the block perpendicularly), and etc.
