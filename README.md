# data_driven_magnetic_soft_material_design

Public code repository for the source code and dataset of the "Data-driven design of shape-programmable magnetic soft materials" paper.

## (1) System requirements

We have tested on Ubuntu 22.04.3 LTS in Python 3.10 (on PC with i7-1165G7 @ 2.80GHz × 8, and 32 GB RAM). While the example codes and development is made on PC with a mall number of cores (4-16), the main run files of the demonstrations are run within a cluster environment on 51 cores, 100 GB RAM (Ubuntu 22.04.3 LTS in Python 3.10). It is suggested to run with a high number of cores (>25) for feasible run times. 


## (2) Python requirements

The required libraries for Python are included in the "requirements.txt". It can be installed within the desired environment (preferably in a virtual environment) from the terminal:

```
pip install -r requirements.txt
```

The installation time should not take more than 15 mins on average.

## (3) Example

The run.py can be run for a simplified demo case in the main repository folder:

```
python3.10 run.py
```

The results will be saved under the /results/example_demo.

Under the /script folder, all the run files (.sh scripts) for the demonstration in our paper can be found. We have also added 'example_local_run.sh' file as a simplified demo case. To run these scripts, you should navigate to "/script" folder on the terminal:

```
cd script
```
The absolute path parameter (2nd line --run_abs_path  "/your/path/to/this/repo/data_driven_magnetic_soft_material_design" \) within the .sh files should be changed according to your repository path, then .sh scripts can be run.
For example, for example_local_run.sh;

```
./example_local_run.sh 
```
The other cases can be run similarly.


## (4) Simulation environment "Voxelyze" with magnetic force and torque

This part is based on the following version of "Voxelyze" 
```
https://github.com/skriegman/evosoro
```
We already compiled it, and this part could be considered as a black box. There is no need to recompile it. But, in case you need to,

Navigate to the _voxcad directory:

```
cd MagSoRo/_voxcad/
```

The following command compiles both VoxCad and Voxelyze, installing the library at the same time:

```
./rebuild_everything.sh
```

The following libraries are a must,

```
sudo apt-get install libqt5-dev qt5-qmake libqwt-dev freeglut3-dev zlib1g-dev
```

There could be other library dependencies that we are unaware of at the moment.

## (5) Dataset for magnetic soft robots and materials

We share the simulation results of the “Data-driven design of shape-programmable magnetic soft materials” work at the following link;

```
https://keeper.mpdl.mpg.de/d/146520950c3b4774afae/
```
It involves a raw dataset of 53 learning runs (resulting in ~1.5e7 simulation evaluations) conducted for the demonstrations and algorithm benchmarking cases. 
Each data provides the position information of the robot in cartesian coordinates along its body at the final steady-state shape for a given design and actuation signal. The dataset is shared to enable further research in stimuli-responsive soft robotics and soft materials fields. 

