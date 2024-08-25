**Fork from University of Canterbury [Seed Tracking Project](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking)**

# Seed Tracker

- [Seed Tracker](#seed-tracker)
- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [On a regular computer for development](#on-a-regular-computer-for-development)
  - [On the main RPI](#on-the-main-rpi)
  - [On the worker RPI](#on-the-worker-rpi)
- [Deploy on production](#deploy-on-production)
- [The CLI (Command Line Interface), for admin user](#the-cli-command-line-interface-for-admin-user)
- [Development of the Seed Tracker](#development-of-the-seed-tracker)
  - [Application Structure](#application-structure)
    - [`actions`](#actions)
    - [`args.py`](#argspy)
    - [`interfaces`](#interfaces)
    - [`background_substraction_pipeline`](#background_substraction_pipeline)
    - [`server_lib`](#server_lib)
    - [`rpi_lib`](#rpi_lib)
    - [`camera_lib`](#camera_lib)
    - [`common_layers` \& `optimizers`](#common_layers--optimizers)
    - [`computations`](#computations)
    - [`resource_manager.py`](#resource_managerpy)
  - [Improve algorithms](#improve-algorithms)
    - [Improve The Seed Position Algorithm](#improve-the-seed-position-algorithm)
    - [Improve the Data Cleaner Algorithm](#improve-the-data-cleaner-algorithm)
    - [Improve The Velocity Algorithm](#improve-the-velocity-algorithm)
    - [Testing your new algorithms](#testing-your-new-algorithms)
- [Survival guide](#survival-guide)


# Introduction

This is the main repository for the Seed Tracker project. Which is an open source instrument for recording seed velocity dropped from a column. 

# Getting Started
  This guide will show you how to quickly install the repo on your Raspberry Pi and starting to use it.


## Prerequisites
  A ssh connection to the Raspberry Pi is required. Your raspberry must be also connected to each other via a network.

  To install the python environnment juste run the `install.sh` script. It will install all the required packages for the project. 


## On a regular computer for development
  After you configure the `config.json` correctly (see [here](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Quick-Start-(Using-the-Instrument)/The-config-file)). 

  You'll be able to start the server as a development one, with mocked interfaces in order to develop the algorithms. 


## On the main RPI
  After you configure the `config.json` correctly (see [here](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Quick-Start-(Using-the-Instrument)/The-config-file)). 

  If you have also started the worker server, you can start playing with the cli (see [CLI](# The CLI (Command Line Interface), for admin user))

## On the worker RPI
  After you configure the `config.json` correctly (see [here](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Quick-Start-(Using-the-Instrument)/The-config-file)). 

  On the worker you just need to start the listener server worker. You can do this by running the following command:
  ```bash
  ./seed-eater-bash -s 
  ```

  You can also program the worker to start the listener server worker on boot. To do this, you can add the following line to the `rc.local` file. 
  ```bash
  /absolut_path_to_your_repo/seed-eater-bash -s
  ```


# Deploy on production

 > See the wiki [here](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Quick-Start-(Building-the-instrument)/Production-setup)



# The CLI (Command Line Interface), for admin user
 > See the wiki [here](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Quick-Start-(Using-the-Instrument)/CLI-Commands)
  

  But basically you can run the following commands : 
  ```bash
  ./seed-eater-bash 
  ```

  and put options you want to run the tool you  want to use.

  Use `./seed-eater-bash -h` to see the help message.

# Development of the Seed Tracker

## Application Structure

### `actions`
The `actions` module contains the implementation of all features of the app.

- `calibrate.py`: Contains functions for single and stereo camera calibration.
- `calculate.py`: Contains functions for calculating seed velocity (not the algorithm but the link between the algorithm and the interface). It also calculates the real-world position of the seed.
- `single/multiple_shot.py`: Contains functions for taking single and multiple shots from the camera, relying on the `camera_lib` module.
- `plot.py`: Contains functions for various plots used by other modules.
- ...

### `args.py`
Handles command-line arguments and configurations.

### `interfaces`
Defines interfaces for algorithm definitions and image processing pipeline abstraction.

### `background_substraction_pipeline`
This is a concrete implementation of the `Processor` interface defined in the `interfaces` module. It is a pipeline that isolates the background from the image. It is composed of multiple layers that are applied sequentially to the input image.

You can create your own pipeline in a new folder, implement the `Processor` interface, and switch to your own pipeline. (Note: This is not an algorithm, so you need to change it manually in the code.)

- `__init__.py`: Initializes the background subtraction pipeline with various processing layers.
- `layers/`: Contains individual processing layers such as `GrayScaleLayer`, `BackgroundRemovalLayer`, `ContrastLayer`, `ThresholdLayer`, `BlurLayer`, and `MergeShapeLayer`.

### `server_lib`
The server library is the interface between `server.py` and the application itself. The main files are `device.py` and `record_launching.py`, which represent the instrument and the record launching. These link all actions together to output the seed velocity as a `Record` object result.

### `rpi_lib`
Handles interaction with hardware modules on the Raspberry Pi, such as the light (LED stripe), the buzzer, or the LCD display. If you specify `linux` as the `hardware` variable in the config file, it will trigger mock functions instead of the real ones.

### `camera_lib`
Contains libraries for camera interactions. Function abstractions are used to provide different camera libraries for different platforms.

### `common_layers` & `optimizers`
- `common_layers`: Contains common processing layers used across different pipelines. You can add your own layers here and use them in the pipeline.
- `optimizers`: Used to optimize a processor before running. It takes a `Processor` and performs some pre-processing on it.

### `computations`
Contains algorithms for computations related to seed tracking.

### `resource_manager.py`
The resource manager processes the config file and provides the configuration to the different modules.

## Improve algorithms

  The Seed Tracker which is the set of algorithms that are used to track the seed, get its world position and compute the velocity are in work in progress.
  Meaning that their all can be easily improved. All algorithms are dynamicly imported from the `src/computations` folder. And their are all following same rules :
  - They are all object oriented, all their class are named `Computer` and they all have a `compute` method.
  - They are all derived from a computing type interface which are defined in the `src/interfaces/*_computing`. 
  - Their constructor tooks a kwargs which is a dictionary of the parameters that are used by the algorithm. Parameters are not defined so feel free to add any parameter you want.
  - Parameters can be set in the `config.json` file (see here)
  - 
### Improve The Seed Position Algorithm
  To improve the seed position algorithm, which deals with taking an image and return the seed position in the image coordinate or None if there is no seed in the image.
  The `Computer` object must be derived from the `ImageComputer` interface (`src/interfaces/image_computing/image_computer`).
  
### Improve the Data Cleaner Algorithm
  Data Cleaner algorithm is performed just after seed position algorithm and right before the velocity algorithm. It is used to clean the data and remove the noise. The `Computer` object must be derived from the `DataCleaner` interface (`src/interfaces/numerical_computing/data_cleaner`). It's main role it's to detect outliers detected by the seed position algorithm and remove them.

### Improve The Velocity Algorithm
  For the velocity algorithm, which takes world seed positions and return the velocity and the error of the velocity. The `Computer` object must be derived from the `VelocityComputer` interface (`src/interfaces/numerical_computing/velocity_computer`).

### Testing your new algorithms
  A test module has been included for testing the algorithms. The test will search for zip samples in the `test` folder. You can find samples here : . You can also create your own samples by zipping a folder containing images (They must keep the same name convention as our solution). You also need to add a file inside called `test` which contains : 
  ```plaintext
  m:x,s:x,v:x
  ``` 
  m stand for the number of seeds in the main images, s for the number of seeds in the worker images and v for the velocity of the seeds. If you don't know the real velocity of the seed on the sample you can put `-1`.

  To run the test you can run the following command : 
  ```bash
  ./test-bash
  ```

# [Survival guide](https://eng-git.canterbury.ac.nz/fgi18/seed-tracking/-/wikis/Misc/Survival-Guide)
