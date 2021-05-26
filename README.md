# Violin SuperPlots: Visualising replicate heterogeneity in large datasets #

![Current exemplary superplot](Violin_SuperPlot_v0-8.png "Violin SuperPlot example")

This work builds upon the SuperPlots proposed by Lord et al. (2020) in "SuperPlots: Communicating reproducibility and variability in cell biology". We propose replacing the underlying beeswarm plot with a modified violinplot while keeping the error bars and scatterpoints for each replicate mean/median. This modified SuperPlot serves to improve readabiliity of dense datasets and allow rapid interpretation of the contribution of cell-level data to the summary statistics.

The package can be installed by running `pip install superviolin`. It can be used as a CLI app to generate Violin SuperPlots or imported into your own scripts to allow extension and customization of the `Superviolin` class.

### Dependencies ###
- appdirs
- click
- matplotlib
- numpy
- openpyxl
- pandas
- scikit-posthocs
- scipy
- xlrd
