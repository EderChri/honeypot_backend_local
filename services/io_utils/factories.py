from services.io_utils.fileloader import FileLoader
from services.io_utils.filewriter import FileWriter


class LoaderFactory:
    @staticmethod
    def get_loader(loader_type):
        match loader_type:
            case "File":
                return FileLoader()
            case _:
                raise ValueError("Unsupported loader type")


class WriterFactory:
    @staticmethod
    def get_writer(writer_type):
        match writer_type:
            case "File":
                return FileWriter()
            case _:
                raise ValueError("Unsupported writer type")
