*When using this package to generate Violin SuperPlots for your publications, please cite the [commentary](https://www.molbiolcell.org/doi/10.1091/mbc.E21-03-0130) from the authors*

## Superviolin CLI commands

`demo`
This command creates a Violin SuperPlot using dummy data that ships with the package. Run superviolin demo from your command prompt after installation to be sure the package is working.

`init`
The superviolin init command generates an "args.txt" file in the current directory, which will be used to generate a Violin SuperPlot based on the Excel or csv file of your data located in the same folder using arguments specified in this text file.

`plot`
The superviolin plot command renders the Violin SuperPlot as a figure. This layout can be edited prior to saving.

If any of these commands results in an error, **please email Martin Kenny** with a copy of:

1. The data that caused the error

2. The accompanying args.txt file

3. A txt file containing the console output

## Superviolin with scripts
You can also import the package into your own Python scripts. Simply import the`Superplot` class by running`from superviolin import Superplot`, and you can begin to automate generation of Violin SuperPlots or extend the `Superplot` class with your own customizations.
