import QtQuick
import QtQuick.Window 2.15
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs

ApplicationWindow {
    title: qsTr("Importer excel")
    width: 800
    height: 580
    visible: true
    flags: Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.CustomizeWindowHint | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint

    Material.theme: Material.Dark
    Material.accent: Material.LightBlue

    property string userName: ""

    RowLayout {
        anchors.fill: parent;
        Pane {
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;
            anchors.horizontalCenter: parent.horizontalCenter
            Text {
                id: userNameText
                text: userName
                color: Material.color(Material.Indigo)
                font.pointSize: 12
                verticalAlignment: Text.AlignVCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }

            FileDialog {
                id: excelFileDialog
                title: qsTr("Sélectionner un fichier excel")
                nameFilters: [ "All files (*)"]
                onAccepted: {
                    console.log("You chose file : " + excelFileDialog.currentFile)
                    appBackend.get_excel(excelFileDialog.currentFile)
                }
                onRejected: {
                    console.log("Canceled")
                }
            }

            Button {
                id: loginButton
                text: qsTr("Sélectionner un fichier excel")
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 15
                onClicked: excelFileDialog.visible = true
            }
        }
    }

    Connections {
        target: appBackend
    }
}