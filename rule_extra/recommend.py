import json
import sys
from verdict import *
import os

if __name__ == '__main__':
    query_file_name = 'intxt.txt'
    verdict1 = Verdict()
    verdict1.read_from_txt(query_file_name)

    corpus_path = 'extract_l3_cases_new'
    num_file = len(os.listdir(corpus_path))
    score = [0] * num_file
    filenames = []
    count = 0
    for ind, filename in enumerate(os.listdir(corpus_path)):
        verdict2 = Verdict()
        verdict2.read_from_txt(os.path.join(corpus_path, filename))
        """
        score[ind] = verdict1.similarity(verdict2)
        print(ind)
        print(filename)
        print(score[ind])
        """
        root = verdict2.treeRoot
        defendantArgument = root.getSonByName('被告辩称:\n')
        
        
        enjoyRights = defendantArgument.getSonByName('是否享有著作权:\n')
        #enjoyRights = defendantArgument.getSonByName('是否构成侵权行为:\n')
        
        
        #otherPerson = enjoyRights.getSonByName('是否有其他权利人":\n')
        #otherPerson = enjoyRights.getSonByName('是否是适格主体:\n')
        #otherPerson = enjoyRights.getSonByName('著作权是否有效:\n')
        #otherPerson = enjoyRights.getSonByName('是否适用于著作权:\n') 
        if enjoyRights.value != '':
            print(filename)
            count += 1
            print(enjoyRights.value)
            print('\n')
        filenames.append(filename)
        del verdict2  
    print(count)
    #for i in range(num_file):
    #    print('%s : %s' % (filenames[i], score[i]))
    index = sorted(range(len(score)), key=score.__getitem__, reverse=True)
    for i in range(10):
        print('%s : %s' % (filenames[index[i]], score[index[i]]))


