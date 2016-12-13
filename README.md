# CLEF eHealth 2016 Task3
__Evaluation with python package trectools__

This repository contains a single script (eval_clef2016.py) that generates a set of graphs with showing the results of many metrics both from the baseline and participant runs for CLEF eHealth 2016 Task 3.

### Dependences:

The two main dependences required are:

1. [trectools](https://github.com/joaopalotti/trec_tools), a python package made for experimental IR. We used trectools version 0.29 in this repository.
You can install this package in your python environment with:
```
pip install trectools
```

2. [ubire](https://github.com/ielab/ubire), a framework used to linearly combine assessments for different relevance dimensions (in this work, we combined topical relevance with understandability and trustworthiness). There is not need for any installation. It is provided in this repository the jar file used to generate the current results.

### Using:
```
python eval_clef2016.py <subtasknumber> <path_to_runs> <output_dir>

Example:
>> python eval_clef2016.py 2 runs2 out_runs2

```

This script will then generate the graphs contained in directory out_runs2.


### Tips:

The current ubire.jar provides a simple combination of scores for different dimensions of relevance modifying the RBP implementation. 

A vanilla RBP would have the following formula to calculate the utility of a rank:

```tex
RBP(p):  (1-p) * \sum_{i=0}{d} rel_i * p^{i-1}
```

In special, for the contribution of document D, retrieved at rank R with an RBP parameter p is given by:
```tex
Contribution (doc, R, p) = rel_doc * p^{R-1}
```
The current version of Ubire will linearly combine the scores of another dimension D as following:
```tex
Contribution (doc, R, p) = Dimension(doc) * rel_doc * p^{R-1}
```
Dimension(doc) is just the assessed understandability or trustworthiness of the documents.
Therefore a highly relevant document (rel_doc = 2) with a high understandability score (let's say U=0.90) retrieved at rank position 3 would have the following contribution to the final RBP with p=0.80:

Contribution(doc, 3, 0.80) = 0.9 * 2 * (0.8)^{2} = 1.15

Note that the same document would have a contribution of 1.28 if understandability was not used.

For more information we redirect the reader to [this ECIR paper.](http://link.springer.com/chapter/10.1007/978-3-319-30671-1_21)

