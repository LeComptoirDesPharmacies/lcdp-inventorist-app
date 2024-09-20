from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtQml import QQmlApplicationEngine
import requests
import uuid
from business.services.assembly import get_assembly_output
from backend.app import open_file
import os
from business.services.excel import dict_to_excel
import platform

def open_directory(directory: str):
    try:

        os.startfile(directory)
    except OSError:
        raise Exception("Impossible d'ouvrir le dossier Téléchargements.")


class MyPythonObject(QObject):
    downloadFinished = Signal(bool)
    downloadStatusChanged = Signal(str)  # Nouveau signal pour mettre à jour le texte


    @Slot(str)
    def downloadFile(self, id: str):
        try:
            print("Assembly id: {}".format(id))

            output = get_assembly_output(id)
            print("OUTPUT: {}".format(output))

            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            download_file = os.path.join(download_path, 'Rapport de {}.xlsx'.format(id))

            print("download file: {}".format(download_file))

            excel = dict_to_excel(download_file, output)

            # print("Writting ...")
            # with open(download_file, 'wb') as f:
            #     f.write(excel.encode('utf-8'))
            # print("Finish")

            open_file(download_file)


            self.downloadFinished.emit(True)
        except Exception as e:
            print(f"Erreur lors du téléchargement : {e}")
            self.downloadFinished.emit(False)
            self.downloadStatusChanged.emit(f"Erreur : {str(e)}")

    @Slot(object)
    def test(self, model):
        print("model: {}".format(model))