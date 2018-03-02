import common as cmn
import integrate
import os
import logging
import time
import sys

"""
main module, program will be run through this module
"""


def main():
    """
    Run program
    """
    cmn.make_dir(cmn.LOG_DIR)
    logging.basicConfig(
        # filename=os.path.join(cmn.LOG_DIR, cmn.LOG_FILE_NAME % time.strftime(cmn.LOG_FILE_NAME_TIME)),
        handlers=[
            logging.FileHandler(os.path.join(cmn.LOG_DIR, cmn.LOG_FILE_NAME % time.strftime(cmn.LOG_FILE_NAME_TIME))),
            logging.StreamHandler()
        ],
        level=cmn.LOG_LEVEL,
        format=cmn.LOG_MSG_FORMAT,
        datefmt=cmn.LOG_TIME_FORMAT
    )

    start_time = time.time()
    logging.info("Starting program ...")

    r, h = False, False

    if "-r" in sys.argv:
        logging.info("Detected 'raw data' command line argument, program will integrate raw counts (non-normalized).\n")
        r = True  
    if "-h" in sys.argv:
        logging.info("Detected 'headers' command line argument, program will add headers to integrated files.\n")
        h = True   
    else:
        logging.warning("No valid command line arguments, program will ignore arguments.\n")
        integrate.run(False)

    integrate.run(r, h)
        

    logging.info("Finished running program.")
    run_time = time.time() - start_time
    logging.info("Total run time: %s.\n" % time.strftime('%H:%M:%S', time.gmtime(run_time)))


if __name__ == "__main__":
    main()
