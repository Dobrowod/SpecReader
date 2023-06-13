"""
@author: danieldobrowolski
contact: dobrowod@mcmaster.ca
"""
import glob
import os
import shutil
import copy
import fnmatch

version_number = 0.3

def while_func(data, k):
    if data[k][0] == '#L':
        return True
    else:
        test = data[k][0].replace('.','')
        return test.isnumeric()

def FullReader(file_raw,scan_start, scan_end, scan_label,spacing):
        data = []
        with open(file_raw,'r') as data_file:
            for line in data_file.readlines():
                data.append(line.split(' '))
            data_file.close()   
        current_scan = 0
        k = 0
        while k < len(data) and current_scan<=scan_end:
            if data[k][0]=='#S':
                current_scan += 1
                if scan_start<=current_scan<=scan_end and (current_scan - scan_start)%spacing == 0: 
                    while data[k][0] != '#L':
                        k+=1
                    outfile=open(file_raw + "_" + scan_label + '_Scan'+str(current_scan)+'.txt','a')
                    while while_func(data,k):
                        if data[k][0] == '#L':
                            for f in range(1,len(data[k])-1):
                                outfile.write(data[k][f]+' ')
                            data[k][-1] = data[k][-1].replace('\n','   \n')
                            outfile.write(data[k][-1])
                        else:
                            for x in range(len(data[k])-1):
                                outfile.write(data[k][x]+' ')
                            data[k][-1] = data[k][-1].replace('\n',' \n')
                            outfile.write(data[k][-1])
                        k+=1
                    outfile.close()
                else:
                    k+=1
            else: 
                k += 1
        print('\n.txt files created')
    
def ScanSelector(raw_name,rows,move_ques):
    ask = 0
    for file_true in glob.glob('*.txt'): 
        i = 0
        array = []
        checking = 0
        cwd = os.getcwd()
        file_name = file_true.replace('.txt','')
        with open(file_true,'r') as data_file:
            for line in data_file.readlines():
                i+= 1
                if i == 1:
                    array.append(line.split('  '))
                    if ask == 0 and len(rows) == 0:
                        print('The columns in the file are as follows:')
                        for j in range(len(array[0])-1):
                            print("For ",array[0][j],"type",str(j))
                        ask += 1
                        columns = input("Input which data/normalization columns you would like to keep, separated by commas: ")
                        rows.append(columns.split(','))
                        for i in range(len(rows[0])):
                            rows[0][i] = int(rows[0][i])
                        move_ques = input("\nWould you like to remove the full scan .txt files? (y/n) ")
                else:
                    array.append(line.split(' '))
            data_file.close()
        if move_ques != 'y' and move_ques != 'yes' and move_ques != 'ye':
           try:
               os.mkdir(cwd+'/FullScans_'+raw_name)
           except FileExistsError:
                pass
        max_index = len(array[0])
        rows_altered = copy.deepcopy(rows)   
        while checking < max_index:
            if checking in rows_altered[0]:
                checking += 1
            else:
                for k in range(len(array)):
                    array[k].pop(checking)
                max_index -= 1
                for l in range(len(rows_altered[0])):
                      rows_altered[0][l] -= 1
        outfile=open(file_name+'.csv','w')
        for m in range(len(array)):
            for p in range(len(array[0])-1):
                outfile.write(array[m][p]+",")
            outfile.write(array[m][-1]+'\n')
        outfile.close()
        if move_ques != 'y' and move_ques != 'yes' and move_ques != 'ye':
            shutil.move(file_true,cwd+'/FullScans_'+raw_name)
        else:
            os.remove(file_true)
    print('\ncsv files created')
    return rows, move_ques.lower()
    
def Normalization(norm_columns,untouched_columns):
    ask = 0
    for file_true in glob.glob('*.csv'): 
        array = []
        file_name = file_true.replace('.csv','') + '_Normalized'
        with open(file_true,'r') as data_file:
            for line in data_file.read().splitlines():
                array.append(line.split(','))
        if ask == 0 and len(norm_columns)==0:
            ask +=1
            for j in range(len(array[0])):
                print("For ",array[0][j],"type",str(j))
            norms = input("Input which normalization columns you would like to use, separated by commas: ")
            norm_columns.append(norms.split(',')) 
            untouched = input("Input which columns you would like to NOT normalize, separated by commas: ")
            untouched_columns.append(untouched.split(','))
        for l in range(len(array[0])):
            if str(l) not in untouched_columns[0] and str(l) not in norm_columns[0]:
                for o in range(1,len(array)):
                    for p in norm_columns[0]:
                        nume = float(array[o][l])
                        denom = float(array[o][int(p)])
                        array[o][l] = str(nume/denom)
                array[0][l] = array[0][l] + '/'
                for u in norm_columns[0]:
                    array[0][l] = array[0][l] + array[0][int(u)] + ' '
                                     
        outfile=open(file_name+'.csv','w')
        for m in range(len(array)):
            for p in range(len(array[0])):
                if str(p) not in norm_columns[0]:
                    outfile.write(array[m][p]+",")
            outfile.write('\n')
        outfile.close()
    print('\nnormalized files created')
    return norm_columns,untouched_columns


###End of Functions###

print('SpecReader V',version_number,'\nThis script is currently confirmed fully compatible with the following beamline SPEC formats: \nCHESS ID4B,ID2A \nCLS 10ID-2\nAPS 29-ID-C,D\nThough it should be compatible with other formats.\n')
more = 'y'
while more == 'y' or more == 'yes' or more == 'ye':
    raw_name = str(input('\nPlease type Spec file name: '))
    num_intervals = int(input('\nHow many scan ranges would you like to process\n(All scans will be processed with the same parameters you input for the first set of scans): '))
    scan_to_do =[[0]*2]*num_intervals
    for b in range(num_intervals):
        print('Set',b+1)
        scan_to_do[b] = [int(input("Start and end (separated by enter): ")) for i in range(2)]
    spacing = int(input("What is the spacing between relevant scans (default =1, all scans): ")) or int(1)
    scan_label = str(input('What would you like to label your scan?: ') or 'scan')
    
    file_path = os.path.realpath(__file__)
    spec_name = os.path.basename(__file__)
    os.chdir(file_path.replace(spec_name,''))
    
    cwd = os.getcwd()
    dir_name = cwd+'/Processed_'+raw_name+'_'+scan_label
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        pass
    shutil.copyfile(raw_name,dir_name+'/'+raw_name)
    os.chdir(dir_name)
    
    rows = []
    move_ques = 'n'
    norms = []
    untouched = []
    for e in range(num_intervals):
        FullReader(raw_name,scan_to_do[e][0],scan_to_do[e][1],scan_label,spacing)
        if e == 0:
            rows, move_ques = ScanSelector(raw_name,rows,move_ques)
        else:
            ScanSelector(raw_name,rows,move_ques)
            
        if e == 0:
            normie = str(input('\nWould you like to normalize your scans (y/n)? '))
            normie = normie.lower()
            
        if normie == 'y' or normie == 'yes' or normie == 'ye':
            if e == 0:
                norms,untouched = Normalization(norms,untouched)
            else:
                Normalization(norms,untouched)
            if e == 0:
                dupes = str(input('\nWould you like to remove the non-normalized files (y/n)? '))
                dupes = dupes.lower()
                if dupes != 'y' and dupes != 'yes' and dupes != 'ye':
                    try:
                        os.mkdir(dir_name+'/SelectScans_'+raw_name)
                    except FileExistsError:
                         pass
                    
            try:
                os.mkdir(dir_name+'/NormedScans_'+raw_name)
            except FileExistsError:
                 pass
            for norm_file in glob.glob('*.csv'): 
                if fnmatch.fnmatch(norm_file, '*.csv'):
                    if not fnmatch.fnmatch(norm_file, '*Normalized.csv'):
                        if dupes == 'y' or dupes == 'yes' or dupes == 'ye':
                            os.remove(norm_file)
                        else:
                            shutil.move(norm_file,dir_name+'/SelectScans_'+raw_name)
                    else:
                        shutil.move(norm_file,dir_name+'/NormedScans_'+raw_name)
                            
    
    remove = str(input('\nWould you like to remove '+raw_name+' from the parent directory \n(Do not remove if you have more scans to process in this file) (y/n)? '))
    remove = remove.lower()
    if remove == 'y' or remove == 'yes' or remove == 'ye':
        os.chdir('..')
        os.remove(raw_name)
    more = str(input('\nWould you like to process another scan or file?(y/n) '))
    more = more.lower()
    os.chdir('..')

print('\nThis was made for fun to avoid responsibility, if you somehow get your hands on it and have bugs or edge cases to report please send them to dobrowod@mcmaster.ca')
