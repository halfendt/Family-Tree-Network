# Family-Tree-Network
Family tree network builder

Python code to injest family history GEDCOM archive file and generate a network graph displaying the connections between individuals in the family tree.

To build the network graph, generate GEDCOM file with individuals using your genealogy software of choice, and run the following in the command line.

For a 3D network graph, run:
```console
python family_tree_network.py -f GEDCOM_filename.ged -d 3
```
or for a 2D network graph, run:
```console
python family_tree_network.py -f GEDCOM_filename.ged -d 2
```

This code with generate a csv file with IDs, names, birth dates, birth places, death dates, and death places for each individual in the family tree file.  Then a network graph html page will load in your browser and you can examine the connections.  Each node represents one individual and hovering over a node will display the name and birth and death dates, if known.
