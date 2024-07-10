from services.io_utils.fileloader import FileLoader
from services.io_utils.filewriter import FileWriter


class LoaderFactory:
    @staticmethod
    def get_loader(loader_type):
        if loader_type == "File":
            return FileLoader()
        else:
            raise ValueError("Unsupported loader type")


class WriterFactory:
    @staticmethod
    def get_writer(writer_type):
        if writer_type == "File":
            return FileWriter()
        else:
            raise ValueError("Unsupported writer type")
