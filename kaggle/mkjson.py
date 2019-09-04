import json 
import subprocess
import os 
# Kernal Metadata 
# https://github.com/Kaggle/kaggle-api/wiki/Kernel-Metadata 

# Kaggle API 
# https://github.com/Kaggle/kaggle-api 
data = {}

data['id'] = 'randomsolution/2019-02-06-linear-regression'
data['title'] = '2019-02-06-linear-regression'
data['code_file'] = '2019-02-06-linear-regression.ipynb'
data['language'] = 'python'
data['kernel_type'] = 'notebook'
data['is_private'] = False
data['enable_gpu'] = False
data['enable_internet'] = True
data['dataset_soruces'] = []
data['competition_sources'] = []
data['kernel_sources'] = []
data['competition_sources'] = []

print(data)

#change to working directory 
path_to_kernel = # redacted 
os.chdir(path_to_kernel)
print("Current Working Directory ", os.getcwd())

with open("kernel-metadata.json",'w') as outfile:
    json.dump(data, outfile, indent='')

response = subprocess.check_output(["kaggle", "kernels", "push", "-p", path_to_kernel]).decode('utf-8')
print(response)
