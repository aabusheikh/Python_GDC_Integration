# Copyright (C) 2018  Ahmad A. A. (https://github.com/bbpgrs/)

import common as cmn
import os
import logging
import pandas as pd

#TODO: comments/doc


def init_integrated_file(type, init_to):
    """

    :param type:
    :param r:
    :param init_from:
    :return:
    """        
    out_lines = []
    init_from = cmn.RNA_LIST_PATH
    if type.upper() == "MIRNA":
        init_from = cmn.MIRNA_LIST_PATH
    with open(init_from, 'r') as in_file:
        for in_line in in_file.readlines():
            gene_name = in_line.split()[0]
            if (type.upper() == "RNA" and gene_name.startswith("E")) or (type.upper() == "MIRNA" and gene_name.startswith("hsa")):
                out_lines.append(gene_name)

    with open(init_to, 'w') as out_file:
        out_file.write("\n".join(out_lines))


def file_name_end(type, r):
    """

    :param type: String 'RNA' or 'miRNA'
    :param r: Boolean raw counts files if true, or normalized if false
    :return:
    """
    s = ""
    if type.upper() == "RNA":
        s = cmn.RNA_FILE_END
    elif type.upper() == "MIRNA":
        s = cmn.MIRNA_FILE_END
    else:
        logging.error("Invalid file type in integrate.py -> fileNameExt()")
        return s

    if not r:
        s += cmn.NORMALIZED_END

    return s


def read_col(type, r):
    """

    :param type: String 'RNA' or 'miRNA'
    :param r: Boolean raw counts files if true, or normalized if false
    :return:
    """
    c = 1
    if not r:
        if type.upper() == "RNA":
            c = 2
        elif type.upper() == "MIRNA":
            c = 4

    return c


def integrate(type, r, h):
    """
    integrate counts files into 1 file per cancer type and gender

    :param type: String 'RNA' or 'miRNA'
    :param r: Boolean raw counts files if true, or normalized if false
    :return:
    """
    logging.info("Integrating %s data files - Use raw data: %s ..." % (type, r))

    for cancer_type in cmn.list_dir(cmn.DL_DIR):
        for gender in cmn.list_dir(os.path.join(cmn.DL_DIR, cancer_type)):

            logging.info("Integrating files in '%s' > '%s' ... \n" % (cancer_type, gender))            

            samples_path = os.path.join(cmn.DL_DIR, cancer_type, gender)            
            samples = [ss for ss in cmn.list_dir(samples_path) if os.path.isdir(os.path.join(samples_path, ss))]
            num_samples = len(samples)
            sn = 1
            _n = 0

            normalized = "normalized"
            if r:
                normalized = "raw"
            integrated_file = os.path.join(samples_path, cmn.INTEGRATED_FNAME
                                           % (cancer_type.lower(), gender.lower(), type.lower(), normalized))

            if not os.path.isfile(integrated_file):                

                logging.info("Initializing integrated file ...")
                init_integrated_file(type, integrated_file)
                logging.info("Loading integrated file into memory as DataFrame ...")
                df = pd.read_csv(integrated_file, sep="\t", header=None, index_col=0)

                for sample in samples:

                    logging.info("Processing sample [%s out of %s (%s > %s)] '%s' ..."
                                 % (sn, num_samples, cancer_type, gender, sample))

                    found_flag = False
                    for file in cmn.list_dir(os.path.join(samples_path, sample)):
                        file_path = os.path.join(samples_path, sample, file)
                        if file.endswith(file_name_end(type, r)):
                            found_flag = True
                            logging.info("Found %s type data file, processing ..." % type)
  
                            logging.info("Integrating file into DataFrame '%s' ..." % file)

                            aa = [in_line.split()[read_col(type, r)]
                                  for in_line in open(file_path, 'r').readlines()
                                  if in_line.startswith("E") or in_line.startswith("hsa")]
                            df.insert(_n, "s%s" % _n, aa) 

                            logging.info("File copied to DataFrame.\n")

                            _n += 1

                    if not found_flag:
                        logging.info("Sample has no file of type %s.\n" % type)

                    sn += 1

                logging.info("Writing integrated DataFrame to file '%s' ..." % integrated_file)
                if not h:
                    df.to_csv(integrated_file, sep="\t", header=None)
                else:
                    df.to_csv(integrated_file, sep="\t")
            else :
                logging.info("Integrated file for %s > %s already exists." % (cancer_type, gender))

            logging.info("Integrated file for %s > %s done.\n" % (cancer_type, gender))


def run(r=False, h=True):
    """
    run module

    :param r: Boolean integrate raw counts if true, or normalized if false
    :return:
    """
    integrate("RNA", r, h)
    integrate("miRNA", r, h)
