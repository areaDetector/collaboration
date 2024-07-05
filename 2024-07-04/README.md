# AD profiling test
This folder contains a basic IOC with the following plugins:
SimDetector,Proc,Roi and transform.

The test was done at a frame rate of 194hz (period set to .005) and a frame
size of 1280x960.

The following commands were used to create the frame graph
```bash
# does profiling
sudo perf record -a -g -p $IOCPID
# convert perf.data to script format
perf script -i perf.data > perf.script
# get FlameGraph
git clone https://github.com/brendangregg/FlameGraph
# create the flame graph
FlameGraph/stackcollapse-perf.pl perf.script | FlameGraph/flamegraph.pl > perf.svg
```
