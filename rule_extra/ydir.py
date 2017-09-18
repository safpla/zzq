# coding:utf-8
#__author__ = 'yhk'

from __future__ import print_function
import os

# return filename and filepath
def get_filename_path(rootdir):
    l_filename=[]
    l_filepath=[]
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            filepath=os.path.join(parent,filename)
            try:
                decode_filename=filename.decode("GB2312")
                decode_filepath=filepath.decode("GB2312")
            except UnicodeDecodeError:
                decode_filename=filename.decode("utf-8")
                decode_filepath=filepath.decode("utf-8")
            l_filename.append(decode_filename)
            l_filepath.append(decode_filepath)
    return l_filename, l_filepath


# 解决中文文件名的编码问题，兼容windows和Linux
def get_filename_from_dir(dir_path):
    file_list=[]
    filepath_list=[]
    if not os.path.exists(dir_path):
        return file_list

    for item in os.listdir(dir_path):
        filepath=os.path.realpath(item) # file absolute path  path mayber wrong 是程序当前的绝对路径+当前文件名
        basename=os.path.basename(item) # filename

        # windows下文件编码为GB2312，Linux下为utf-8
        try:
            decode_str=basename.decode("GB2312")
            decode_path=filepath.decode("GB2312")
        except UnicodeDecodeError:
            decode_str=basename.decode("utf-8")
            decode_path=filepath.decode("utf-8")

        file_list.append(decode_str)
        filepath_list.append(decode_path)
    return file_list, filepath_list

# 创建目录
def mkdir(path):
    path=path.strip()
    path=path.rstrip("\\")  # 去除尾部\符号
    isExists=os.path.exists(path)
    if not isExists: # 如果不存在则创建目录
        os.makedirs(path)
        return True
    else:
        return False


if __name__=='__main__':
    # test function: get_filename_from_dir
    rootdir='cases'
    filenames, filepaths=get_filename_from_dir(rootdir)
    for filename,filepath in  zip(filenames,filepaths):
        print("%s--%s" % (filename, filepath))


















