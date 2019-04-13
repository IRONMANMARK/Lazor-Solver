# Lazor
This is a project for Software Carpentry, Spring 2019.
The goal of this project is to build up a code that will automatically find solutions to the “Lazor” game on phones.
## How to use
The only thing that need to change is the the path for the folder that contain all the .bff file.<br>
## Highlights
* The folder don't need to be a exclusive folder for the bff file. The folder can have different kind of file in it and the code can run properly.<br>
* The out file is automatically generated and put into the same folder with all the input bff file.<br>
* The code can run super fast. It only take `65.23 seconds` to `solve all 8 level` and output to a file.
## Notice
* The input file must be .bff in certain format.
* In the output file:<br>
  > o: blocks allowed<br>
  > x: no block allowed<br>
  > A: reflect block<br>
  > B: opaque block<br>
  > C: refract block<br>
* This code apply for Lazor boards with reflect, refract, and opaque blocks only. It does not include solutions with black hole blocks(which teleport the laser from one block to another) and diamond blocks(the laser enter the block perpendicularly), and etc.
