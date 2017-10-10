import spider
import statistics
import export
import os
import subprocess

"""
Script to run every day
"""

# update aircraft where type and operator is missing
spider.update_new_acs_info()

# aggregate statistics of mdl, typ, and airlines
statistics.aggregate()

# export data
project_path = os.path.dirname(os.path.realpath(__file__))
subprocess.call("bash %s/export.sh" % project_path, shell=True)
