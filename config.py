import configparser

# khởi tạo thông tin từ file config
def init(file_path):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    return config
