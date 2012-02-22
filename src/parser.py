#####
# Parse simple model descriptions from a CSV file into JSON
#
# Caveat: Does not handle complex soil (multiple soil profiles)
#
#####

import csv
import json

## GLOBALS
data_cols = [5,16]
"""A list of columns in the CSV where data is defined"""
in_complex = False
"""Complex mode binary switch"""

def handle_data(line, d, t):
    """
    Process a line of data from a specially formatted CSV file.

    If the first entry in the line matches the data_col then enter
    complex mode to read that line as new column headers. Otherwise
    set first entry as a variable name with data as the data_cols.

    @type  line: list
    @param line: A line of data from the CSV
    @type     d: dictionary
    @param    d: Put the processed information into this dictionary
    @type     t: string
    @param    t: The top level key under L{d}
    """
    global in_complex
    if(not in_complex):
        key = set_simple_key(line)
        complex_keys = []
        for idx, col in enumerate(data_cols):
            if(line[col] != ''):
                if(line[col].lower() != key):
                    d[idx][t][key] = convert_type(line[col])
                else:
                    handle_data.complex_key_map[line[0]] = set_complex_keys(line, col)
                    for i in range(len(data_cols)):
                        d[i][t][line[0]] = []
                    in_complex = True
    else:
        complex_keys = handle_data.complex_key_map[line[0]]
        for idx, col in enumerate(data_cols):
            if(line[col] != ''):
                complex_data = line[col:(col+len(complex_keys))]
                for i,ld in enumerate(complex_data):
                    complex_data[i] = convert_type(ld)
                d[idx][t][line[0]].append(dict(zip(complex_keys, complex_data)))

handle_data.complex_key_map = {}
"""The static key map foex key headers"""

def convert_type(data):
    """
    Convert string to proper number if appropriate
    """
    try:
        v = float(data)
        return v
    except ValueError:
        return data


def set_simple_key(line):
    """
    Set the key for a given data line

     @type  line: list
     @param line: A line of simple (flat) data.
     @rtype: string
     @return: The key name extracted from the data
    """
    return line[1].lower();

def set_complex_keys(line, offset):
    """
    Set complex keys from a given data line

    @type    line: list
    @param   line: A line of complex data
    @type  offset: integer
    @param offset: The offset of the column starting the complex key
    @rtype: list
    @return: The compelx keys extracted from the data
    """
    keys = []
    for idx, data in enumerate(line):
        if(idx >= offset):
            if(data != ""):
                keys.append(data.lower())
            else:
                return keys
def main():
    """
    Main control loop of the parser. Maintains state with current_module variable.
    """
    global in_complex
    reader = csv.reader(open('silver_sample.csv', 'rU'))
    exp1 = {'meta': {}, 'management': {}, 'observed': {}, 'weather': {}, 'soil':{}}
    exp2 = {'meta': {}, 'management': {}, 'observed': {}, 'weather': {}, 'soil':{}}
    experiments = [exp1,exp2]
    for row in reader:
        if(row[0] == 'Metadata'):
            handle_data(row, experiments, 'meta')
        elif(row[0] == 'CropMgmt'):
            handle_data(row, experiments, 'management')
        elif(row[0] == 'Observed'):
            handle_data(row, experiments, 'observed')
        elif(row[0].startswith('Weather')):
            handle_data(row, experiments, 'weather')
        elif(row[0].startswith('Soil')):
            handle_data(row, experiments, 'soil')
        else:
            if(in_complex):
                in_complex = False
    print 'Process completed'
    print '#########'
    print json.dumps(experiments[0])
    print '#########'
    print json.dumps(experiments[1])
    """Only dumping JSON temporarily as an exmaple dataset"""

if __name__ == '__main__':
    main()
