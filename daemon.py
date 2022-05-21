"""here will be the daemon service class
    """
# def created_file_handler(event):
#     if event.is_directory == False:
#         with FileCoder(configuration.passwd, configuration.salt) as coder:
#             coder.encode_file(event.src_path)

if __name__ == '__main__':
    pass
    # my_listener = PathListener(created_file_handler,on_modified=print, path=configuration.pysafe_dir)
    # try:
    #     my_listener.start_listening()
    #     while True:
    #         sleep(1)
    # except KeyboardInterrupt:
    #     del my_listener