# EMS Bus

Experimental support for control of Worcester Bosch type boilers using EMS 2-wire bus.

In order to send and receive commands to and from the serial interface a 'stub' is required:
  
1. Compile using - sudo gcc emsctl_2.c -o emsctl
2. Make executable using - sudo chmod +x emsctl
3. Make available using - sudo cp emsctl /usr/bin
