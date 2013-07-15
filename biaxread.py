import numpy as np
import sys
import struct

def ReadAscii(f_name):
    """
    Takes a filename containing the text output (with headers) from xlook and
    reads the columns into a rec array for easy data processing and access.
    """

    filename = f_name

    f = open(filename,'r')
    
    col_width = 12 # Columns are 12 char wide in header
    
    # First line of the file is the number of records
    num_recs = f.readline()
    num_recs = int(num_recs.strip('number of records = '))
    print "\nNumber of records: %d" %num_recs
    
    # Second line is column numbers, we don't care so just count them
    num_cols = f.readline()
    num_cols = num_cols.split('col')
    num_cols = len(num_cols)
    print "Number of columns: %d" %num_cols
    
    # Third line is the column headings
    col_headings_str = f.readline()
    col_headings_str = col_headings_str[5:-1]
    col_headings = []
    for i in xrange(len(col_headings_str)/12):
        heading = col_headings_str[12*i:12*i+12].strip()
        col_headings.append(heading)

    # Fourth line is column units
    col_units_str = f.readline()
    col_units_str = col_units_str[5:-1]
    col_units=[]
    for i in xrange(len(col_units_str)/12):
        heading = col_units_str[12*i:12*i+12].strip()
        col_units.append(heading)
    col_units = [x for x in col_units if x != '\n']  #Remove newlines
    
    # Fifth line is number of records per column
    col_recs = f.readline()
    col_recs = col_recs.split('recs')
    col_recs = [int(x) for x in col_recs if x != '\n']
    
    # Show column units and headings
    print "\n\n-------------------------------------------------"
    print "|%15s|%15s|%15s|" %('Name','Unit','Records')
    print "-------------------------------------------------"
    for column in zip(col_headings,col_units,col_recs):
        print "|%15s|%15s|%15s|" %(column[0],column[1],column[2])
    print "-------------------------------------------------"
    
    # Read the data into a numpy recarray
    dtype=[]
    dtype.append(('row_num','float'))
    for name in col_headings:
        dtype.append((name,'float'))
    dtype = np.dtype(dtype)
    
    data = np.zeros([num_recs,num_cols])
    
    i=0
    for row in f:
        row_data = row.split()
        for j in xrange(num_cols):
            data[i,j] = row_data[j]
        i+=1
    data_rec = np.rec.array(data,dtype=dtype)
    
    f.close()
    
    return data_rec

def ReadBin(f_name):
    """
    Takes a filename containing the binary output from xlook and
    reads the columns into a rec array for easy data processing and access.
    """
    
    filename = f_name

    f = open(filename,'rb')
    
    col_headings = []
    col_recs     = []
    col_units    = []
    
    name = struct.unpack('20c',f.read(20))
    name = ''.join(str(i) for i in name)
    name = name.split("\0")[0]
    print "\nName: ",name
    
    num_recs = struct.unpack('>I',f.read(4))
    num_recs = int(num_recs[0])
    print "Number of records: %d" %num_recs
    
    num_cols =  struct.unpack('>I',f.read(4))
    num_cols = int(num_cols[0])
    print "Number of columns: %d" %num_cols
    
    swp =  struct.unpack('>I',f.read(4))[0]
    print "Swp: ",swp
    
    dtime =  struct.unpack('>I',f.read(4))[0]
    print "dtime: ",dtime
    
    
    for i in range(32):
        chname = struct.unpack('13c',f.read(13))
        chname = ''.join(str(i) for i in chname)
        chname = chname.split("\0")[0] 
        
        chunits = struct.unpack('13c',f.read(13))
        chunits = ''.join(str(i) for i in chunits)
        chunits = chunits.split("\0")[0]
    
        
        gain = struct.unpack('>I',f.read(4))
    
        
        comment = struct.unpack('50c',f.read(50))
        comment = ''.join(str(i) for i in comment)
    
    
        nelem = struct.unpack('>I',f.read(4))
        nelem = int(nelem[0])
        
        if chname[0:6] == 'no_val':
            continue
        else:
            col_headings.append(chname)
            col_recs.append(nelem)
            col_units.append(chunits)
    
    
    # Show column units and headings
    print "\n\n-------------------------------------------------"
    print "|%15s|%15s|%15s|" %('Name','Unit','Records')
    print "-------------------------------------------------"
    for column in zip(col_headings,col_units,col_recs):
        print "|%15s|%15s|%15s|" %(column[0],column[1],column[2])
    print "-------------------------------------------------"
    
    # Read the data into a numpy recarray
    dtype=[]
    #dtype.append(('row_num','float'))
    for name in col_headings:
        dtype.append((name,'float'))
    dtype = np.dtype(dtype)
    
    data = np.zeros([num_recs,num_cols])
    
    for col in range(num_cols):
        for row in range(col_recs[col]):
            data[row,col] = struct.unpack('<d',f.read(8))[0]

    data_rec = np.rec.array(data,dtype=dtype)
    
    f.close()
    
    return data_rec