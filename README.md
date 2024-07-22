# Seed Tracker

- [Seed Tracker](#seed-tracker)
- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [On a regular computer for development](#on-a-regular-computer-for-development)
  - [On the Master RPI](#on-the-master-rpi)
  - [On the Slave RPI](#on-the-slave-rpi)
- [The CLI (Command Line Interface), for admin user](#the-cli-command-line-interface-for-admin-user)
- [Development of the Seed Tracker](#development-of-the-seed-tracker)
  - [Improve The Seed Position Algorithm](#improve-the-seed-position-algorithm)
  - [Improve the Data Cleaner Algorithm](#improve-the-data-cleaner-algorithm)
  - [Improve The Velocity Algorithm](#improve-the-velocity-algorithm)
  - [Testing your new algorithms](#testing-your-new-algorithms)


# Introduction

This is the main repository for the Seed Tracker project. Which is an open source instrument for recording seed velocity dropped from a column. 

# Getting Started
  This guide will show you how to quickly install the repo on your Raspberry Pi.


## Prerequisites
  A ssh connection to the Raspberry Pi is required. Your raspberry must be also connected to each other via a network.

  To install the python environnment juste run the `install.sh` script. It will install all the required packages for the project. 

## On a regular computer for development

## On the Master RPI


## On the Slave RPI
  After you configure the `config.json` correctly (see [here](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Quick-Start-(Using-the-Instrument)/The-config-file)). 

  On the slave you just need to start the listener server worker. You can do this by running the following command:
  ```bash
  ./seed-eater-bash -s 
  ```

  You can also program the slave to start the listener server worker on boot. To do this, you can add the following line to the `rc.local` file. 
  ```bash
  /absolut_path_to_your_repo/seed-eater-bash -s
  ```


  



# The CLI (Command Line Interface), for admin user
 > See the wiki [here](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Quick-Start-(Using-the-Instrument)/CLI-Commands)
  

  But basically you can run the following commands : 
  ```bash
  ./seed-eater-bash 
  ```

  and put options you want to run the tool you  want to use.

  Use `./seed-eater-bash -h` to see the help message.

# Development of the Seed Tracker

  The Seed Tracker which is the set of algorithms that are used to track the seed, get its world position and compute the velocity are in work in progress.
  Meaning that their all can be easily improved. All algorithms are dynamicly imported from the `src/computations` folder. And their are all following same rules :
  - They are all object oriented, all their class are named `Computer` and they all have a `compute` method.
  - They are all derived from a computing type interface which are defined in the `src/interfaces/*_computing`. 
  - Their constructor tooks a kwargs which is a dictionary of the parameters that are used by the algorithm. Parameters are not defined so feel free to add any parameter you want.
  - Parameters can be set in the `config.json` file (see here)
  - 
## Improve The Seed Position Algorithm
  To improve the seed position algorithm, which deals with taking an image and return the seed position in the image coordinate or None if there is no seed in the image.
  The `Computer` object must be derived from the `ImageComputer` interface (`src/interfaces/image_computing/image_computer`).
  
## Improve the Data Cleaner Algorithm
  Data Cleaner algorithm is performed just after seed position algorithm and right before the velocity algorithm. It is used to clean the data and remove the noise. The `Computer` object must be derived from the `DataCleaner` interface (`src/interfaces/numerical_computing/data_cleaner`). It's main role it's to detect outliers detected by the seed position algorithm and remove them.

## Improve The Velocity Algorithm
  For the velocity algorithm, which takes world seed positions and return the velocity and the error of the velocity. The `Computer` object must be derived from the `VelocityComputer` interface (`src/interfaces/numerical_computing/velocity_computer`).

## Testing your new algorithms
  A test module has been included for testing the algorithms. The test will search for zip samples in the `test` folder. You can find samples here : . You can also create your own samples by zipping a folder containing images (They must keep the same name convention as our solution). You also need to add a file inside called `test` which contains : 
  ```plaintext
  m:x,s:x,v:x
  ``` 
  m stand for the number of seeds in the master images, s for the number of seeds in the slave images and v for the velocity of the seeds. If you don't know the real velocity of the seed on the sample you can put `-1`.

  To run the test you can run the following command : 
  ```bash
  ./test-bash
  ```