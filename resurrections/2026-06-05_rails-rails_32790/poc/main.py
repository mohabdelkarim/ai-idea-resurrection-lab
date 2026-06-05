import os
import uuid
import hashlib

class Folder:
    def __init__(self, name, parent=None):
        self.id = uuid.uuid4()
        self.name = name
        self.parent = parent
        self.files = {}
        self.folders = {}

    def add_file(self, file_name, file_content):
        file_id = hashlib.sha256(file_name.encode()).hexdigest()
        self.files[file_id] = file_content

    def add_folder(self, folder):
        self.folders[folder.id] = folder

    def get_folder(self, folder_id):
        return self.folders.get(folder_id)

    def list_files(self):
        return list(self.files.keys())

    def list_folders(self):
        return list(self.folders.keys())

class Service:
    def __init__(self, root_folder):
        self.root_folder = root_folder

    def upload_file(self, folder_id, file_name, file_content):
        folder = self.root_folder
        folder_ids = folder_id.split('/')
        for id in folder_ids:
            if id:
                folder = folder.get_folder(id)
                if not folder:
                    raise ValueError(f'Folder {id} not found')
        folder.add_file(file_name, file_content)

    def create_folder(self, parent_folder_id, folder_name):
        parent_folder = self.root_folder
        folder_ids = parent_folder_id.split('/')
        for id in folder_ids:
            if id:
                parent_folder = parent_folder.get_folder(id)
                if not parent_folder:
                    raise ValueError(f'Folder {id} not found')
        new_folder = Folder(folder_name, parent_folder)
        parent_folder.add_folder(new_folder)
        return new_folder.id

def main():
    root_folder = Folder('root')
    service = Service(root_folder)

    try:
        folder_id = service.create_folder('', 'images')
        service.upload_file(folder_id, 'image1.png', b'file_content1')
        service.upload_file(folder_id, 'image2.png', b'file_content2')

        folder_id = service.create_folder(folder_id, 'products')
        service.upload_file(folder_id, 'product1_image.png', b'file_content3')
        service.upload_file(folder_id, 'product2_image.png', b'file_content4')

        print('Files in root folder: ', root_folder.list_files())
        print('Folders in root folder: ', root_folder.list_folders())
        images_folder = root_folder.get_folder(folder_id.split("/")[0])
        print('Files in images folder: ', images_folder.list_files())
        print('Folders in images folder: ', images_folder.list_folders())
        products_folder = images_folder.get_folder(folder_id.split("/")[1])
        print('Files in products folder: ', products_folder.list_files())
        print('Folders in products folder: ', products_folder.list_folders())
    except Exception as e:
        print(f'Error: {e}')