import common as cmn
import os
import logging
import pandas as pd

#TODO: comments/doc


def init_integrated_file(type, r, init_from):
    """

    :param type:
    :param r:
    :param init_from:
    :return:
    """
    samples_path = os.path.split(os.path.split(init_from)[0])[0]
    cancer_type = os.path.split(os.path.split(samples_path)[0])[1]
    gender = os.path.split(samples_path)[1]

    normalized = "normalized"
    if r:
        normalized = "raw"

    file_name = cmn.INTEGRATED_FNAME % (cancer_type.lower(), gender.lower(), type.lower(), normalized)
    file_path = os.path.join(samples_path, file_name)

    out_lines = []
    with open(init_from, 'r') as in_file:
        for in_line in in_file.readlines():
            gene_name = in_line.split()[0]
            if (type.upper() == "RNA" and gene_name.startswith("E")) or (type.upper() == "MIRNA" and gene_name.startswith("hsa")):
                out_lines.append(gene_name)

    with open(file_path, 'w') as out_file:
        out_file.write("\n".join(out_lines))

    return file_path


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


def copy_file(rcol, file_path, copy_path):
    """

    :param rcol:
    :param wcol:
    :param file_path:
    :param copyPath:
    :return:
    """
    out_lines = []
    with open(file_path, 'r') as in_file, open(copy_path, 'r') as out_file:
        for in_line in in_file.readlines():
            if in_line.startswith("E") or in_line.startswith("hsa"):
                read_value = in_line.split()[rcol]

                # TODO: remove
                #logging.debug("read value: %s" % read_value)

                out_line = out_file.readline().split()
                out_line.append(read_value)
                out_line = "\t".join(out_line)
                out_lines.append(out_line)

                # TODO: remove
                #logging.debug("adding line: %s" % out_line)

    with open(copy_path, 'w') as out_file:
        out_file.write("\n".join(out_lines))


def add_header(file_path, num_samples):
    """
    """
    if os.path.isfile(file_path) and file_path.endswith((cmn.INTEGRATED_FNAME % ("", "", "", "")).replace("_", "")):
        df = pd.read_csv(file_path, sep="\t", header=None, index_col=0, names=["s%s" % sn for sn in range(1, num_samples+1)])
        (f_path, f_name) = os.path.split(file_path)
        f_name = "%s_HEADERS.%s" % (f_name[0:f_name.rfind(".")], f_name[f_name.rfind("."):])
        new_path = os.path.join(f_path, f_name)
        df.to_csv(new_path, sep="\t")


def integrate(type, r):
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

            integrated_file = ""
            init_flag = False

            samples_path = os.path.join(cmn.DL_DIR, cancer_type, gender)            
            samples = [ss for ss in cmn.list_dir(samples_path) if os.path.isdir(os.path.join(samples_path, ss))]
            num_samples = len(samples)
            sn = 1

            for sample in samples:

                logging.info("Processing sample [%s out of %s (%s > %s)] '%s' ..." % (sn, num_samples, cancer_type, gender, sample))

                found_flag = False
                for file in cmn.list_dir(os.path.join(samples_path, sample)):
                    file_path = os.path.join(samples_path, sample, file)
                    if file.endswith(file_name_end(type, r)):
                        found_flag = True
                        logging.info("Found %s type data file, processing ..." % type)

                        if not init_flag:
                            logging.info("Initializing integrated file ...")
                            integrated_file = init_integrated_file(type, r, file_path)
                            init_flag = True

                        logging.info("Integrating file '%s' ..." % file)

                        copy_file(read_col(type, r), file_path, integrated_file)

                        logging.info("File copied.\n")

                if not found_flag:
                    logging.info("Sample has no file of type %s.\n" % type)

                sn += 1
            
            #logging.info("Adding headers to file %s" % integrated_file)
            #add_header(integrated_file, num_samples)

            logging.info("Integrated file for %s > %s done.\n" % (cancer_type, gender))


def run(r=False):
    """
    run module

    :param r: Boolean integrate raw counts if true, or normalized if false
    :return:
    """
    integrate("RNA", r)
    integrate("miRNA", r)
