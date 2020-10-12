# Code for running and analyzing simulations for the manuscript: Models with Multiple Snow Layers Are Essential to Improve Snow Predictions in Current and Future Climates

## Background & contact
This repo contains eveything except for the compiled SUMMA model to reproduce the results from the manuscript.
If you have any questions feel free to open an issue or contact us!

 * Andrew R Bennett (andrbenn@uw.edu)
 * Nicoleta C. Cristea (cristn@uw.edu)

## Getting started
We ran SUMMA as released in version 3.0.1. To reproduce our results you will
first have to install SUMMA, and then run the simulations.  The code to run
the simulations is found in the `run_simulations` directory.

## run_simulations

To run the simulations you should only have to run through the two contained notebooks.
First you will have to run the `run_simulations` notebook. Following the completion of
the simulations (which may take a long time if you are on a small machine) you can merge
the datasets together to prepare for running the analysis. Once you've run these you can
perform the analysis in the `gen_plots` directory.

## gen_plots

This directory contains the notebooks which can be used to generate the plots for the paper.
It can only be run after the notebooks in `run_simulations` are complete,
as we do note include the simulation output in the repo to save space.
Each notebook generates a set of plots which have similar types. Run each of them
to produce all of the analysis plots from the paper.

## Supporting code/data

This is a brief summary of the remaining directories:

* `lib`: contains library functions which are shared by other notebooks, or just to be abstracted away
* `obs_data`: contains observation data
* `processed`: a placeholder directory for putting merged datasets
