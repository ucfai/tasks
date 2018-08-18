# SIGAI@UCF's `admin` module

Basically, to make everything jive really well together, 
[@ionlights][@gh-ionlights] put this together to make most tasks 
needed to maintain the non-content-generating portions of the club highly 
structured so that bots could handle a lot of the "heavy-lifting" in terms of 
maintenance. 

This repo is compose of a few different "submodules":
- `algorithms` houses reference implementations of just about every kind of 
algorithm we've covered in previous semesters, rather highly commented, too. :smiley: 
- `animations` is our custom animation library (creds: [@thedibaccle][@gh-thedibaccle], 
and [@ionlights][@gh-ionlights])
- `arcc` is how we manage interaction with ARCC's cluster and make SSH'ing dead-
simple.
- `env` houses environment files to run this, on all mainstream OSes the 
coordinators have tended to run in the past.
- `jupyter` holds onto all the Jupyter configuration files/folders. This 
actually should make its way into the group folder on the ARCC cluster, whenever
changes are propogated, but we keep it here for reference.
- `notebooks` handles the construction, updating, and conversion of any group's
semester notebooks (largely for use on the website), although TravisCI tends to
run this most times.
- `semester` is the programmatic way to generate all the needed files for new 
semester, along with structuring notebooks and other templated files for 
relatively easy use among Coordinators and students alike.  

[@gh-ionlights]: https://github.com/ionlights
[@gh-thedibaccle]: https://github.com/thedibaccle
