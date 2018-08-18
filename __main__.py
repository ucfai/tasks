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
    
    parser.add_argument("op", choices=["make", "update", "jekyll"],
                        help="Choose the action to perform on a semester.")
    
    parser.add_argument("topic", choices=["data-science", "intelligence",
                                          "course"], help="Select the topic to "
                                                          "perform `op` on.")
    
    parser.add_argument("semester", help="Specified semester to perform `op` "
                                         "on.")
    
    logging.basicConfig(format="%(levelname)10s | %(message)s",
                        filename="admin/logs/notebooks.log",
                        level=logging.DEBUG)
    
    args = parser.parse_args()
    
    semester = semester.S(args.semester, args.topic, cwd)
    eval("semester._" + args.op)()
