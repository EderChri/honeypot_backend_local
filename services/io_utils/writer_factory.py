from services.io_utils.filewriter import FileWriter


class WriterFactory:
    @staticmethod
    def get_writer(writer_type):
        if writer_type == "File":
            return FileWriter()
        else:
            raise ValueError("Unsupported writer type")
