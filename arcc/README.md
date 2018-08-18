## `arcc` submodule

ARCC is UCF's 'Advanced Research Computing Center'; basically, it houses the 
supercomputers we've been graciously afforded access to. However, their 
automated key-generation and such falls just a tad short. To avoid chaining/
typing out long SSH commands, we auto-generate `config` files for the students.

As requested by ARCC, nothing useable is specified in these files for attack 
vectors. Don't become lazy and put those values in them, it's a very bad idea and 
ultimately may cost us the ability to use these (which really makes lectures-
workshops) more entertaining and significantly easier to maintain.

This should be run once a semester, prior to handing out keys to the students 
so that they can access the servers. :thumbsup:
