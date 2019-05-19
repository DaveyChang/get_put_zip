# -*- coding:utf-8 -*-

import socket
import paramiko
import os
from stat import *
from zipfile import ZipFile
import shutil


class ExportPrepare(object):

    def __init__(self, ip, port, username, password):
        self.ip = socket.gethostbyname(ip)
        self.port = port
        self.username = username
        self.password = password

    # make a connection to sftp
    def sftp_con(self):
        try:
            t = paramiko.Transport((self.ip, self.port))
            t.connect(username=self.username, password=self.password)
            return t
        except Exception as e:
            print("sftp_con: ", e)

    # find all files to upload
    def __get_all_files_in_local_dir(self, local_dir):
        all_files = list()
        if os.path.exists(local_dir):
            files = os.listdir(local_dir)
            for x in files:
                filename = os.path.join(local_dir, x)
                # print("filename:" + filename)
                # isdir
                if os.path.isdir(filename):
                    all_files.extend(self.__get_all_files_in_local_dir(filename))
                else:
                    all_files.append(filename)
        else:
            print('{}does not exist'.format(local_dir))
        return all_files

    # find all files to download
    def __get_all_files_in_source_dir(self, sftp, source_dir):
        all_files = list()
        if source_dir[-1] == '/':
            source_dir = source_dir[0:-1]
        files = sftp.listdir_attr(source_dir)
        for x in files:
            filename = source_dir + '/' + x.filename
            if S_ISDIR(x.st_mode):
                all_files.extend(self.__get_all_files_in_source_dir(sftp, filename))
            else:
                all_files.append(filename)
        return all_files

    # Copy a local file (local_dir) to the SFTP server as remote_dir
    def sftp_put_dir(self, local_dir, remote_dir):
        try:
            # put local_dir files to remote_dir
            t = self.sftp_con()
            sftp = paramiko.SFTPClient.from_transport(t)
            if remote_dir[-1] == '/':
                remote_dir = remote_dir[0:-1]
                all_files = self.__get_all_files_in_local_dir(local_dir)
                for x in all_files:
                    filename = os.path.split(x)[-1]
                    remote_file = os.path.split(x)[0].replace(local_dir, remote_dir)
                    path = remote_file.replace('\\', '/')
                    sftp.chdir('/')  # 寻址根目录
                    data = path.split('/')
                    for item in data:
                        try:
                            sftp.chdir(item)
                            # print(u'要上传的目录已经存在，选择性进入合并' + item)
                        except:
                            sftp.mkdir(item)
                            sftp.chdir(item)
                            # print(u'要上传的目录不存在，创建目录' + item)
                    remote_filename = path + '/' + filename
                    # print (u'Put files...' + filename)
                    sftp.put(x, remote_filename)
                print("put file %s done . " % local_dir)
        except Exception as e:
            print('sftp_put_dir: ', e)

    # Copy a SFTP server file (source_dir) to the local as local_dir
    def sftp_get_dir(self, local_dir, source_dir):
        try:
            t = self.sftp_con()
            sftp = paramiko.SFTPClient.from_transport(t)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            else:
                shutil.rmtree(local_dir)
                os.makedirs(local_dir)
            try:
                all_files = self.__get_all_files_in_source_dir(sftp, source_dir)
                for file in all_files:
                    filename = file.split('/')[-1]
                    local_file = os.path.split(file)[0].replace(source_dir, local_dir)
                    path = local_file.replace('/', '\\')
                    if not os.path.exists(path):
                        os.makedirs(path)
                    local_filename = os.path.join(path, filename)
                    # print("Get file ...", filename)
                    sftp.get(file, local_filename)
                print("get file from %s done . " % source_dir)
            except Exception as e:
                print('readfile: ', e)
        except Exception as e:
            print("sftp_get_dir: ", e)

    # zip all download files
    def sftp_get_zip(self, zipfile_dir, getzip_dir, local_dir):
        try:
            if os.path.exists(zipfile_dir):
                shutil.rmtree(zipfile_dir)
            shutil.copytree(local_dir, zipfile_dir)
            shutil.make_archive(getzip_dir, 'zip', getzip_dir)
            # shutil.rmtree(getzip_dir)
            print("打包完成，zip包存放于目录:", getzip_dir)
        except Exception as err:
            print(err)
    
    # zip all local_dir_list files
    def sftp_copy_file_list(self, zipfile_dir, local_dir_list=[]):
        try:
            if os.path.exists(zipfile_dir):
                shutil.rmtree(zipfile_dir)
                os.makedirs(zipfile_dir)
            if not os.path.exists(zipfile_dir):
                os.makedirs(zipfile_dir)
            for local_dir in local_dir_list:
                all_files = self.__get_all_files_in_local_dir(local_dir)
                # print(all_files)
                for file in all_files:
                    filename = file.split('\\')[-1]
                    local_file = os.path.split(file)[0].replace(local_dir, zipfile_dir)
                    if not os.path.exists(local_file):
                        os.makedirs(local_file)
                    local_filename = os.path.join(local_file, filename)
                    shutil.copy(file, local_filename)
            print("copy file done .")

        except Exception as err:
            print(err)

