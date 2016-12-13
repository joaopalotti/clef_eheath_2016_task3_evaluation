import matplotlib
matplotlib.use('Agg')

import os
import sys

import pandas as pd
# trectools can be obtained with pip install trectools
from trectools import procedures
from trectools import TrecQrel

"""
 Reads all .txt files from a directory.
"""

#path_to_runs = "/home/palotti/clef2016/eval/runs1/"
if len(sys.argv) != 4 :
    print "Usage: python eval_clef2016.py <task#> <path_to_runs> <output_dir>"
    sys.exit(1)

else:
    taskNum = int(sys.argv[1])
    path_to_runs = sys.argv[2]
    output_dir = sys.argv[3]

    if os.path.exists(path_to_runs):
        print "Using runs from: %s " % (path_to_runs)
    else:
        print "Could not find directory %s. Aborting..." % (path_to_runs)
        sys.exit(1)

runs = procedures.list_of_runs_from_path(path_to_runs, "*.txt")

"""
Load Qrels:
"""
qrels = TrecQrel("../qrels/task%d.qrels" % (taskNum))
qunder = TrecQrel("../qrels/task%d.qunder" % (taskNum))
qtrust= TrecQrel("../qrels/task%d.qtrust" % (taskNum))
qcomb = TrecQrel("../qrels/task%d.combundertrust.txt" % (taskNum))

print "-- Evaluating with trec_eval..."
evaluation = procedures.evaluate_runs(runs, qrels)

print "-- Evaluating ubire qunder..."
ueval = procedures.evaluate_runs_ubire(runs, qrels, qunder, "under")

print "-- Evaluating ubire qtrust..."
teval = procedures.evaluate_runs_ubire(runs, qrels, qtrust, "trust")

print "-- Evaluating ubire combining both with qunder and qtrust..."
ceval = procedures.evaluate_runs_ubire(runs, qrels, qcomb, "comb")

print "-- Checking QRel coverage at top 10 results..."
covs = procedures.get_coverage(runs, qrels, topX=10)

print "-- Getting evaluation results for regular metrics..."
rmap = procedures.get_results(evaluation, "map")
rp10 = procedures.get_results(evaluation, "P_10")
bpref = procedures.get_results(evaluation, "bpref")
rrbp = procedures.get_results(ueval, "RBP(0.8)")

print "-- Getting results for understandability biased metrics.."
urbp = procedures.get_results(ueval, "uRBP(0.8)")
urbpgr = procedures.get_results(ueval, "uRBPgr(0.8)")

print "-- Getting results for trustworthiness biased metrics.."
trbp = procedures.get_results(teval, "uRBP(0.8)")
trbpgr = procedures.get_results(teval, "uRBPgr(0.8)")

print "-- Getting restuls for combination of both understandability and trustworthiness biased metrics.."
crbp = procedures.get_results(ceval, "uRBP(0.8)")
crbpgr = procedures.get_results(ceval, "uRBPgr(0.8)")


print "-- Generating graphs in dir %s... " % (output_dir)
#
for extension in ["pdf", "png", "svg"]:
    # General
    procedures.plot_system_rank(os.path.join(output_dir,"map." + extension), rmap, "map")
    procedures.plot_system_rank(os.path.join(output_dir,"p10." + extension), rp10, "P@10")
    procedures.plot_system_rank(os.path.join(output_dir,"bpref." + extension), bpref, "bpref")
    procedures.plot_system_rank(os.path.join(output_dir,"rbp." + extension), rrbp, "RBP(0.8)")
    procedures.plot_system_rank(os.path.join(output_dir,"coverages." + extension), covs, "Coverage")

    # Understadability:
    procedures.plot_system_rank(os.path.join(output_dir,"u_rbp." + extension), urbp, "uRBP(0.8)")
    procedures.plot_system_rank(os.path.join(output_dir,"u_rbpgr." + extension), urbpgr, "uRBPgr(0.8)")

    # Trustworthiness:
    procedures.plot_system_rank(os.path.join(output_dir,"t_rbp." + extension), trbp, "tRBP(0.8)")
    procedures.plot_system_rank(os.path.join(output_dir,"t_rbpgr." + extension), trbpgr, "tRBPgr(0.8)")

    # Combined both Understandability adn Trustworthiness:
    procedures.plot_system_rank(os.path.join(output_dir,"c_rbp." + extension), trbp, "cRBP(0.8)")
    procedures.plot_system_rank(os.path.join(output_dir,"c_rbpgr." + extension), trbpgr, "cRBPgr(0.8)")

# -- Done with printing graphs....


"""
Creates a unique merged dataset
"""
maps = pd.DataFrame(rmap, columns=["name","value","ci"])
p10s = pd.DataFrame(rp10, columns=["name","value","ci"])
rbps = pd.DataFrame(rrbp, columns=["name","value","ci"])
bprefs = pd.DataFrame(bpref, columns=["name","value","ci"])
# understandability:
urbps = pd.DataFrame(urbp, columns=["name","value","ci"])
urbpgrs = pd.DataFrame(urbpgr, columns=["name","value","ci"])
# trustworthiness
trbps = pd.DataFrame(trbp, columns=["name","value","ci"])
trbpgrs = pd.DataFrame(trbpgr, columns=["name","value","ci"])
# combination of both understandability and trustworthiness
crbps = pd.DataFrame(crbp, columns=["name","value","ci"])
crbpgrs = pd.DataFrame(crbpgr, columns=["name","value","ci"])

dfcov = pd.DataFrame(covs, columns=["name", "value_cov", "ci_cov"])

merged = pd.merge(p10s, maps, on="name", suffixes=("_p10","_map"))
merged2 = pd.merge(bprefs, rbps, on="name", suffixes=("_bpref","_rbp",))
merged3 = pd.merge(urbps, urbpgrs, on="name", suffixes=("_urbp","_urbpgr"))
merged4 = pd.merge(trbps, trbpgrs, on="name", suffixes=("_trbp","_trbpgr"))
merged5 = pd.merge(crbps, crbpgrs, on="name", suffixes=("_crbp","_crbpgr"))

merged = pd.merge(merged, merged2).merge(dfcov).merge(merged3).merge(merged4).merge(merged5)

print "P@10 results..."
print merged.sort_values("value_p10", ascending=False)[["name","value_p10"]].reset_index(drop=True)

print "MAP results..."
print merged.sort_values("value_map", ascending=False)[["name","value_map"]].reset_index(drop=True)

print "RBP(0.8) results..."
print merged.sort_values("value_rbp", ascending=False)[["name","value_rbp"]].reset_index(drop=True)

print "Pickling dataset..."
merged.to_pickle("merged_df.pickle")

print "All done!"

