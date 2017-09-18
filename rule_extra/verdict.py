#!/home/leo/anaconda2/env/python3/bin/python
# -*- coding: utf-8 -*-
import json
import re
import thulac
import math

thul = thulac.thulac(seg_only=True)

def clean_set(set_all):
    if ',' in set_all:
        set_all.remove(',')
    if '。' in set_all:
        set_all.remove('。')
    if '、' in set_all:
        set_all.remove('、')
    if '的' in set_all:
        set_all.remove('的')

    return set_all

def cos_ab(v1, v2):
    prod_cross = 0.0
    prod_1 = 0.0
    prod_2 = 0.0
    for a, b in zip(v1, v2):
        prod_cross = prod_cross + a * b
        prod_1 = prod_1 + a * a
        prod_2 = prod_2 + b * b

    return prod_cross / (math.sqrt(prod_1) * math.sqrt(prod_2))

def sent_simi(sent1, sent2):
    text1 = thul.cut(sent1)
    text2 = thul.cut(sent2)
    text1 = [t[0] for t in text1]
    text2 = [t[0] for t in text2]
    set1 = {t for t in text1}
    set2 = {t for t in text2}
    set_all = set1 | set2
    set_all = clean_set(set_all)
    list_all = list(set_all)
    list_all.sort()
    vec1 = [0] * len(list_all)
    vec2 = [0] * len(list_all)
    for t in text1:
        if t in list_all:
            vec1[list_all.index(t)] += 1
    for t in text2:
        if t in list_all:
            vec2[list_all.index(t)] += 1
    return cos_ab(vec1, vec2)

def node_similarity(root1, root2):
    if len(root1.getSons()) != len(root2.getSons()):
        print('tree structure dismatch')
        print(root1.key)
        print('root1')
        for son in root1.getSons():
            print(son.key) 
        print('root2')
        for son in root2.getSons():
            print(son.key)

        print(len(root1.getSons()))
        print(len(root2.getSons()))
        return 2
    sons1 = root1.getSons()
    sons2 = root2.getSons()
    num_son = len(sons1)
    simi_son = 0
    for i in range(num_son):
        son1 = sons1[i]
        son2 = sons2[i]
        if son1.key != son2.key:
            print('tree structure dismatch')
            return -1
        temp = node_similarity(son1, son2)
    #print('%d son of %s: %s' %(i, root1.key, temp))
        simi_son += temp
	
    if (root1.value == '') and (root2.value == ''):
        simi_self = 0.5
    elif (root1.value == '') or (root2.value == ''):
        simi_self = 0
    else:
        simi_self = sent_simi(root1.value, root2.value)
    #print('simi_self of %s: %s' %(root1.key, simi_self))
    return (simi_son + simi_self) / (num_son + 1)

class TreeNode():
    def __init__(self, rootObj):
        self.key = rootObj['key']
        self.value = rootObj['value']
        self.sons = []
        self.numSon = 0
        self.father = None
        self.curSon = 0

    def setKey(self, key):
        self.key = key

    def setValue(self, value):
        self.value = self.value + value

    def insertSon(self, son):
        self.sons.append(TreeNode(son))
        self.sons[self.numSon].father = self
        self.numSon += 1

    def getSons(self):
        return self.sons

    def getASon(self,ind):
        if len(self.sons) <= ind:
            print('You don''t have son #%s' % ind)
            return -1
        else:
            return self.sons[ind]

    def getFather(self):
        return self.father

    def getLastSon(self):
        if len(self.sons) < 1:
            print('You don''t have any sons')
            return -1
        else:
            return self.sons[self.numSon - 1]

    def getFirstSon(self):
        if len(self.sons) < 1:
            print('You don''t have any sons')
            return -1
        else:
            return self.sons[0]
	
    def getSonByName(self, name):
        find = False
        for son in self.sons:
            #print(son.key)
            if son.key == name:
                find = True
                return son
        print('You don''t have a son named %s' % name)
        return -1
    
    def getNextSon(self):
        if len(self.sons) <= self.curSon:
            return -1
        else:
            self.curSon += 1
            return self.sons[self.curSon - 1]

    def resetAllCurSon(self):
        self.curSon = 0;
        for son in self.sons:
            son.resetAllCurSon()

class Verdict():
    def __init__(self):
        self.doc = {}
	

    def read_from_txt(self, intxt_file_name):
        fin = open(intxt_file_name, 'r')
        root = TreeNode({'key': 'root', 'value': '判决书'})
        self.treeRoot = root
        indent_level = 0
        re_tabs = re.compile('(^\t*)[^\t\n]+')
        re_cont = re.compile('\t*([^\t]+)')
        for line in fin.readlines():
            tabs = re_tabs.findall(line)
            cont = re_cont.findall(line)
            cont = cont[0]
            if (tabs == []) or (len(cont) < 3):
                    continue
            now_level = len(tabs[0])
            if (cont[-2] == ':') and (cont[-4:-2] != '如下'):
                if now_level == indent_level:
                    root.insertSon({'key': cont, 'value': ''})
                elif now_level > indent_level:
                    if now_level > indent_level + 1:
                        print('wrong structure')
                        return
                    root = root.getLastSon()
                    indent_level += 1
                    root.insertSon({'key': cont, 'value': ''})
                else:
                    while now_level < indent_level:
                        root = root.getFather()
                        indent_level -= 1
                    root.insertSon({'key': cont, 'value': ''})
            else:
                root.getLastSon().setValue(cont)



	
    def read_from_json(self, injson_file_name):
        pass

    def write_to_txt(self, outtxt_file_name):
        fout = open(outtxt_file_name, 'w')
        root = self.treeRoot
        root.resetAllCurSon()
        cur_level = -1
        while root != None:
            son = root.getNextSon()
            if son == -1:
                root = root.getFather()
                cur_level -= 1
            else:
                root = son
                cur_level += 1
                fout.write('\t' * cur_level + root.key)
                sents = root.value.split('\n')
                for sent in sents:
                    fout.write('\t' * cur_level + sent + '\n')
        fout.close()

    def write_to_json(self, outjson_file_name):
        pass
	
		
    def similarity(self, ref_verdict):
        root1 = self.treeRoot
        root2 = ref_verdict.treeRoot
        return node_similarity(root1, root2)

if __name__ == '__main__':
    intxt_file_name = 'extract_l3_cases/intxt.txt'
    reftxt_file_name = 'extract_l3_cases/reftxt5.txt'
    verdict1 = Verdict()
    verdict1.read_from_txt(intxt_file_name)
    verdict2 = Verdict()
    verdict2.read_from_txt(reftxt_file_name)
    print(verdict1.similarity(verdict2))

