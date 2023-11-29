import shutil, os

path = os.path.abspath('.')
cur_floder_name = os.path.basename(path)
deploy_floder_name = f"{cur_floder_name}_deploy"
deploy_path = os.path.join(cur_floder_name, deploy_floder_name)

shutil.rmtree(deploy_path, ignore_errors=True)
os.mkdir(deploy_path)
shutil.copy2(os.path.join(path, 'main.py'), deploy_path)
shutil.copy2(os.path.join(path, 'config.json'), deploy_path)

for folder_name in ['src', 'jscodegen']:
    os.mkdir(os.path.join(deploy_path, folder_name))

    for src_lib in os.listdir(os.path.join(path, folder_name)):
        if src_lib == '__pycache__':
            continue
        shutil.copy2(os.path.join(path, folder_name, src_lib), os.path.join(deploy_path, folder_name))
    
shutil.make_archive(deploy_floder_name, 'zip', deploy_path)
