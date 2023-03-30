# AMiGA

**A**nalysis of **Mi**crobial **G**rowth **A**ssays is a cool tool that you should check out here: [https://github.com/firasmidani/amiga](https://github.com/firasmidani/amiga).

# AMiGA Irregular Time-Points Hack

Currently, AMiGA does not allow analysis of growth curve data that has irregular time intervals. This repository is a fork from the original AMiGA program. It is a *hack* that allows loading of data with arbitrary time points into AMiGA to obtain summary statistics. This fork is intended only as a short-term work-around and not as a stable release. User beware!

Only one well can be run at a time. The data for each well is simply inputted as a `.csv` file (first column: time, second column: baselined OD value). 
