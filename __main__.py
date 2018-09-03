from argparse import ArgumentParser
import os
import logging

from admin import semester

if __name__ == "__main__":
    cwd = os.getcwd()
    parser = ArgumentParser(
            description="Generates the template-ized Jupyter Notebooks we used "
                        "for every lecture and adds in metadata to be used "
                        "when converting given Notebooks into corresponding "
                        "HTML to be posted on the web.")
    
    subparsers = parser.add_subparsers(dest="op")
    
    make = subparsers.add_parser("make",
                                 description="Primary maintenance script, "
                                             "generates `skeletons`, "
                                             "`notebooks`, and `jekyll-posts`. "
                                             "This has been built specifically "
                                             "to only modify what's necessary "
                                             "if files already exist. If you "
                                             "want to restart a specific file, "
                                             "please use `update`.")
    
    update = subparsers.add_parser("update",
                                   description="Update specific files, this "
                                               "tends to be a very destructive "
                                               "process, USE CAUTIOUSLY!")
    
    make_op = make.add_mutually_exclusive_group(required=True)
    make_op.add_argument("--skeleton", action="store_true",
                         help="Generate the skeleton for a given semester.")

    make_op.add_argument("--notebooks", action="store_true",
                         help="Generate the notebooks for a given semester. "
                              "(This requires having already generated a the "
                              "semester's `skeleton`.)")

    make_op.add_argument("--jekyll-posts", action="store_true",
                         help="Convert semester Notebooks into posts suitable "
                              "to be displayed on https://ucfsigai.org/ - this "
                              "should by used whenever you want to convert "
                              "posts, even if there already exists the same "
                              "versions.")

    make_op.add_argument("--banners", action="store_true",
                         help="Generate banners for each meeting in a given "
                              "semester - this will be displayed on "
                              "https://ucfsigai.org/ and the Facebook Group's "
                              "Events.")

    update_op = update.add_mutually_exclusive_group(required=True)
    update_op.add_argument("--notebooks", action="store_true",
                           help="Update the notebooks for a given semester. "
                                "(This requires having already generated a the "
                                "semester's `skeleton`.)")
    
    update_op.add_argument("--skeleton",
                           help="Update one of the skeleton files, keep in "
                                "mind that this will simply overwrite it with "
                                "the default file.")
    
    logging.basicConfig(format="%(levelname)10s | %(message)s",
                        filename="admin/logs/notebooks.log",
                        level=logging.DEBUG)
    
    args = parser.parse_args()
    args = vars(args)
    
    sem = semester.Semester(cwd)
    
    ops = {
        "make": {"notebooks": None, "skeleton": None, "jekyll_posts": None, 
        "banners": None},
        "update": {"notebooks": None, "skeleton": None}
    }
    
    if args["op"] == "make":
        for k, v in args.items():
            if k == "op":
                continue
            if v:
                eval("semester.make_" + k)(sem)
                break
    elif args["op"] == "update":
        if args["notebooks"]:
            semester.update_notebooks(sem)
        else:
            semester.update_skeleton(sem, args["skeleton"])
    else:
        print("Invalid choice, exiting.")
        exit(-1)
