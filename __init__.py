from invoke import Collection

from .src import *

ns = Collection("autobot")

# Custom libraries for Meeting management
ns.add_collection(semester)
# ns.add_collection(solutionbook)
# ns.add_collection(papers)

# Third-party / Custom APIs
# ns.add_collection(hugo)
# ns.add_collection(kaggle)
# ns.add_collection(sendgrid)
# ns.add_collection(youtube)
