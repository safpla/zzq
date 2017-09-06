# -*- coding:utf-8 -*-
import json

def main():
    bullet_path = 'demo/predict.label'
    input_json = 'demo/input.json'
    output_json = 'demo/output.json'

    bullet_stream = open(bullet_path, 'r')
    input_stream = open(input_json, 'r')
    output_stream = open(output_json, 'w')
    guns = json.load(input_stream)
    bullets = bullet_stream.readlines()
    for i in range(len(bullets)):
        bullet = bullets[i].strip()
        if bullet == u'非影视作品':
            guns[i]['DL'] = bullet
        else:
            guns[i]['DL'] = '影视作品'
            guns[i]['XL'] = bullet

    json.dump(guns, output_stream, ensure_ascii=False, indent=2)
    output_stream.close()

if __name__ == '__main__':
    main()
