import common as cmn
import os
import logging


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
            samples = cmn.list_dir(samples_path)
            sn = 1

            for sample in samples:

                logging.info("Processing sample [%s out of %s] '%s' ..." % (sn, len(samples), sample))

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



def run(r=False):
    """
    run module

    :param r: Boolean integrate raw counts if true, or normalized if false
    :return:
    """
    integrate("RNA", r)
