# -*- coding: utf-8 -*-

import numpy as np
import thulac

thu = thulac.thulac(seg_only=True, model_path='thulac_models')
thu.cut_f('data.txt0', 'data.txt1')
