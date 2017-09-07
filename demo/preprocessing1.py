# run in python3
import json
import pickle as pkl
import thulac

def get_data_extract(input_json):
    ft = open('demo/data.txt0', 'w')
    fl = open('demo/data.label', 'w')
    meta_data_path = 'data/meta.pkl'
    meta_data = pkl.load(open(meta_data_path, 'rb'))
    label_class = meta_data['n_y']
    l = [0] * label_class

    f = open(input_json, 'r')
    data = json.load(f)
    for line in data:
        fl.write(''.join([str(ll) for ll in l[1:]]) + '\n')
        ft.write(line['extract'] + '\n')
    ft.close()
    fl.close()

def main():
    input_json = 'demo/input.json'
    output_json = 'demo/output.json'
    get_data_extract(input_json)
    thu = thulac.thulac(seg_only=True, model_path='data/thulac_models')
    thu.cut_f('demo/data.txt0', 'demo/data.txt1')
    print('cut finished')
    exit()

if __name__ == '__main__':
    main()