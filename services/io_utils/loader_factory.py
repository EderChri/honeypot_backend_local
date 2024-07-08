from services.io_utils.fileloader import FileLoader


class LoaderFactory:
    @staticmethod
    def get_loader(loader_type):
        if loader_type == "File":
            return FileLoader()
        else:
            raise ValueError("Unsupported loader type")
