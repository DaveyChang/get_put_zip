# get_put_zip
get from sftp , put on sftp , make a zip

创建对象 sftpIP or 域名，端口号，账号，密码

对象调用函数
sftp_put_dir(本地路径，目标路径) # 上传本地文件到目标路径（sftp）
sftp_get_dir(本地路径，源件目录) # 下载源文件（sftp）到本地路径
sftp_get_zip(存放目录, 打包目录, 本地路径)  # 打包单个路径zip
sftp_copy_file_list(指定路径， 路径列表) # 拷贝路径列表下所有文件及目录到指定路径
