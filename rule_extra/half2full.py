# coding:utf-8
from __future__ import print_function
import os
import codecs
import sys
import ydir
print(sys.getdefaultencoding())
reload(sys)
sys.setdefaultencoding('utf-8')
print(sys.getdefaultencoding())
if __name__ == '__main__':
    """
    folder_name = u'cases'
    new_folder_name = u'cases_new'
    filenames, filepaths = ydir.get_filename_path(folder_name)
    for filename in filenames: 
        print(filename)
        fin = codecs.open(os.path.join(folder_name, filename), 'r', encoding='utf-8')
        fout = codecs.open(os.path.join(new_folder_name, filename), 'w', encoding='utf-8')
        for line in fin.readlines():
            change_flag = False
            for i in range(len(line)):
                if line[i] == u':':
                    new_line = line[:i] + u'：' + line[i+1:]
                    change_flag = True
            if change_flag:
                fout.write(new_line)
            else:
                fout.write(line)
        fin.close()
        fout.close()
    """
    
    folder_name = u'cases'
    filenames, filepaths = ydir.get_filename_path(folder_name)
    for filename in filenames: 
        fin = codecs.open(os.path.join(folder_name, filename), 'r', encoding='utf-8')
        for line in fin.readlines():
            change_flag = False
            for i in range(len(line)):
                if line[i] == u'适格':

                    new_line = line[:i] + u'：' + line[i+1:]
                    change_flag = True
            if change_flag:
                fout.write(new_line)
            else:
                fout.write(line)
        fin.close()
        fout.close()

