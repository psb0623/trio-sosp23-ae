# Artifact Evaluation Submission for ArckFS+ [SOSP '25] 

This repository contains the artifact for reproducing our SOSP '25 paper "Analyzing and Enhancing ArckFS: An Anecdotal Example of Benefits of Artifact Evaluation". 

# Table of Contents
* [Overview](#overview)
* [Setup](#setup)
* [Running experiments](#running-experiments)
* [Known Issues](#known-issues)

# Overview 

### Structure:

```
root
|---- arckfsplus         (source code of arckfs+)
    |---- checker        (verifier source code)
    |---- fsutils        (simple file system commands)         
    |---- include        (header files shared between libfs and kernel module)
    |---- lib            (libraries shared between libfs and kernel module) 
    |---- kfs            (kernel part of arckfs+)
    |---- libfs          (arckfs+ library file system source code)
    |---- libfsfd        (fdfs source code)
    |-----libfskv        (kvfs source code)
    |-----test           (simple testing code for arckfs+)
|---- arckfs             (source code of arckfs)
    |---- fsutils        (simple file system commands)         
    |---- include        (header files shared between libfs and kernel module)
    |---- lib            (libraries shared between libfs and kernel module) 
    |---- kfs            (kernel part of arckfs)
    |---- libfs          (arckfs library file system source code)
    |---- libfsfd        (fdfs source code)
    |-----libfskv        (kvfs source code)
    |-----test           (simple testing code for arckfs)
|---- fs                 (source code of other evaluated file systems)
    |---- odinfs         
    |---- parradm       
    |---- nova         
    |---- pmfs 
    |---- winefs
    |---- strata
    |---- splitfs 
|---- linux              (5.13.13 Linux kernel)
|---- eval               (evaluation)
    |---- benchmark      (source code of workload applications) 
    |---- scripts        (main evaluation scripts) 
    |---- fig            (figures) 
    |---- data           (raw data)
|---- dep.sh             (scripts to install dependency)    
```

### Environment: 

Our artifact should run on any Linux distribution. The current scripts are developed for **Ubuntu 20.04.4 LTS**. Porting to other Linux distributions would require some script modifications, especially ```dep.sh```, which installs dependencies with package management tools.

Our artifact requires a machine equipped with Intel Optane persistent memory.

To run our artifact within a VM to test functionality, see [here](vm/vm.md). 

To run our artifact within a container, please first install the kernel on your
host machine (step 2 below) and then follow the instructions 
[here](container/container.md). 

# Setup 

**Note**: For the below steps, our scripts will complain if they fail to compile or install the target. Check the end part of the scripts' output to ensure that the install is successful. Also, some scripts would prompt to ask the sudo permission at the beginning.

### 1. Install the dependencies:
```
$ ./dep.sh 
```

### 2. Install the 5.13.13 Linux kernel (50GB space and 20 minutes)
```
$ cd linux
$ cp config .config
$ make oldconfig             (update the config with the provided .config file)
```

Say N to KASAN if the config program asks about it. 

```
KASAN: runtime memory debugger (KASAN) [N/y/?] (NEW) N
```


Next, please use your favorite way to compile and install the kernel. The below step is just for reference. The installation requires 50GB space and takes around 20 minutes on our machines. 

For Ubuntu:
```
$ make -j8 deb-pkg           (generate the kernel installment package)
$ cd ..
$ sudo dpkg -i *.deb         (install the package) 
```

Otherwise, the classical ways will work as well:

```
$ make -j8              
$ make -j8 modules
$ sudo make modules_install
$ sudo make install
```
Reboot the machine to the installed 5.13.13 kernel. 

### 3. Install and insmod file systems 

If 5.13.13 kernel is already installed, start from this point.

Set the kernel up for building external modules

```
$ cd linux
$ cp config .config
$ make oldconfig
$ make modules_prepare
```

```
$ cd fs
$ ./compile.sh
```
This script will compile, install, and insert the following kernel modules:

* Odinfs 
* PMFS 
* NOVA 
* Winefs
* SplitFS

Please note that these kernel modules do not persist across machine reboots. Please rerun the above steps every time you boot the kernel. Our experimental scripts will detect this before execution. 

[Expected outputs at the end of the execution](docs/output-fs-compile.md)

```
$ cd fs
$ ./strata.sh
```

This script will install Strata.

```
$ cd fs
$ ./splitfs.sh
```
This script will install SplitFS.

### 4. Install ArckFS, ArckFS+ and FxMark 

#### 4.1 ArckFS

```
$ cd arckfs
$ ./compile.sh
```
[Expected outputs at the end of the execution](docs/output-arckfs-compile.md)

#### 4.2 ArckFS+

```
$ cd arckfsplus
$ ./compile.sh
```

#### 4.3 Fxmark

```
$ cd eval/benchmark/fxmark
$ ./compile.sh
```

**Hardware setup**: 
* Please disable hyperthreading in the BIOS to avoid issues due to CPU pinning before running experiments. 


### 5. Running Experiments

Main scripts are under ```eval/scripts/```.

Please run all scripts with **sudo** privileges.

```
eval/scripts
|---- single-thread.sh          (single thread experiments; section 5.1, fig3)
|---- fxmark.sh                 (Fxmark-related experiments; section 5.2, fig4)
|---- filebench-shared.sh       (filebench-shared experiment; section 5.3)
|---- sharing-cost.sh           (sharing cost experiment; section 5.4, table 4)
|---- run-all.sh                (running all the above scripts)
|---- parse.sh                  (parse and output the results to directory: eval/data)
```

You can use `run-all.sh` for all four experiments. It takes about 12 hours in our machine.
```
$ sudo ./run-all.sh
```

If some experiments fails, you can run each experiment as follows.
``` 
$ sudo ./single-thread.sh
$ sudo ./fxmark.sh
$ sudo ./filebench-shared.sh
$ sudo ./sharing-cost.sh
```

**2. How to check results**

- `single-thread.sh`: run `eval/fig/fig3.py` to draw a figure (raw data are in `eval/data/sg_meta`)
  - Compare: Generated figure (`fig3.pdf`) with Figure 3 in the paper.  
    - ArckFS+ and ArckFS perform better than other secure file systems.  
    - Similar to the paper’s figure, ArckFS+ performs slightly worse than ArckFS. 
- `fxmark.sh`: run `eval/fig/fig4.py` to draw a figure. (raw data are in `eval/data/fxmark`)
  - Compare: Generated figure (`fig4.pdf`) with Figure 4 in the paper.  
    - ArckFS+ and ArckFS perform better than other secure file systems.  
    - Similar to the paper’s figure, ArckFS+ generally performs comparably to ArckFS but slightly worse in some workloads.
- `filebench-shared.sh`: check csv files in `eval/data/filebench-shared`.
  - Expected result: ArckFS+ perform comparable with ArckFS.
  - Relavant text in the paper: "ArckFS+ delivers performance comparable to ArckFS, with relative throughput of 101.1% and 102.1% for a single thread, and 97.1% and 98.8% for 16 threads on the Webproxy and Varmail workloads, respectively."
- `sharing-cost.sh`: run `eval/fig/table4.py` to draw a table (`table4.md`). (raw data are in `eval/data/sharing-cost`)
  - Expected result: tgroup (trust group) results are better than without tgroup, as described in Section 5.4 of the paper. (tgroup results are better than NOVA)
  - Relavant text in the paper: "Concurrent write access to a shared inode incurs a sharing cost for ArckFS+. To reduce this cost, a user can use a trust group, where multiple applications share inodes within the group without verification,"
  - Note: Higher values are better for the top two rows, while lower values are better for the bottom two rows.

# Known issues 

1. The kernel might complain about CPU soft lockup during some experiments. This can be safely ignored. 

2. Filebench installation fails upon the first invocation of ./compile.sh. Rerun ./compile.sh can successfully install filebench

3. ArckFS works by intercepting file system-related system calls. However, some library invokes these system calls during their initialization, before ArckFS can initialize. Fixing this requires enforcing the initialization order of libraries, which, to our understanding, depends on the implementation of the loader and is not always possible. 

4. ArckFS numbers its threads (i.e., the first thread within the process is 0 and the next thread is 1 etc.) based on difference of gettid() and the thread id of the first thread. (With the current Linux, there seems to be no good way to number threads.). If the system is constantly creating a large number of proceses/threads in the background (e.g., running k8s services), ArckFS may panic. A small number of background processes are fine. 

# License

Trio is licensed under Apache License 2.0.
