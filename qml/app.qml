import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs

ApplicationWindow {
    title: qsTr("Le Comptoir Des Pharmacies - Gestionnaire d'inventaire")
    width: 600
    height: 480
    visible: true
    minimumWidth: 600
    minimumHeight: 480

    Material.theme: Material.Light
    Material.accent: '#3AB872'

    property string reportPath: ""
    property string templateUrl: ""
    property string excelPath: ""
    property bool loading: false

    function isEmpty(str){
        return str == ""
    }

    StackView {
        anchors.fill: parent

        initialItem: Page {
            header: Label {
                id: header
                text: qsTr("Gestionnaire d'inventaire")
                bottomPadding: 10
                topPadding: 10
                color: '#3AB872'
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: '#1E276D'
                }
                font.pixelSize: 22
                horizontalAlignment: Text.AlignHCenter
            }
            Pane {
                id: card
                width: parent.width*0.8
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 20
                Material.elevation: 6
                ColumnLayout {
                    id: colLayout
                    spacing: 5
                    anchors.fill: parent
                    Text {
                        id: chooseText
                        text: qsTr("Quel type d'import souhaites-tu faire ?")
                        font.pointSize: 16
                        Layout.fillWidth: true
                        color: '#1E276D'
                        Layout.alignment: "Qt::AlignHCenter"
                    }
                    ComboBox {
                        id: receiptSelector
                        Layout.fillWidth: true
                        width: 80
                        Layout.alignment: "Qt::AlignHCenter"
                        textRole: "text"
                        valueRole: "value"
                        model: appBackend.actions
                        enabled: !loading
                        onActivated: appBackend.select_action(currentValue)
                        Component.onCompleted: currentIndex = indexOfValue("")
                    }
                    RowLayout {
                        visible: !isEmpty(templateUrl)
                        Layout.topMargin: 20
                        spacing: 2
                        Text {
                            id: templateText
                            color: '#1E276D'
                            text: qsTr("Lien template :")
                            font.pointSize: 12
                        }
                        Text {
                            id: templateLink
                            text: '<html><style type="text/css"></style><a href="'+templateUrl+'">Template '+receiptSelector.currentText+'</a></html>'
                            onLinkActivated: Qt.openUrlExternally(templateUrl)
                            font.pointSize: 12
                            wrapMode: Text.WordWrap
                            MouseArea {
                                anchors.fill: parent
                                acceptedButtons: Qt.NoButton
                                cursorShape: Qt.PointingHandCursor
                            }
                        }
                    }
                }
            }
            ColumnLayout {
                id: actionLayout
                anchors.top: card.bottom
                anchors.topMargin: 15
                width: parent.width
                spacing: 5
                Button {
                    id: selectFileButton
                    enabled: !isEmpty(templateUrl)
                    text: qsTr("Sélectionner un fichier excel")
                    onClicked: excelFileDialog.visible = true
                    Layout.alignment: "Qt::AlignHCenter"
                    visible: !loading
                }
                Text {
                    id: excelPathText
                    Layout.preferredWidth: parent.width
                    color: '#1E276D'
                    horizontalAlignment: Text.AlignHCenter
                    text: excelPath
                    font.pointSize: 12
                    wrapMode: Text.WordWrap
                    Layout.alignment: "Qt::AlignHCenter"
                }
                Button {
                    id: startBtn
                    Layout.topMargin: 15
                    text: qsTr("Go !")
                    onClicked: appBackend.start()
                    visible: !isEmpty(excelPath)
                    enabled: !loading
                    Material.background: Material.Teal
                    Layout.alignment: "Qt::AlignHCenter"
                }
                ProgressBar {
                   id: loader
                   indeterminate: true
                   Layout.alignment: "Qt::AlignHCenter"
                   visible: loading
                }
                Text {
                    id: statusText
                    text: qsTr("")
                    color: Material.color(Material.Indigo)
                    font.pointSize: 12
                    Layout.alignment: "Qt::AlignHCenter"
                }
                Button {
                    id: openReport
                    Layout.topMargin: 15
                    text: qsTr("Ouvrir le rapport")
                    onClicked: appBackend.open_file(reportPath)
                    visible: !isEmpty(reportPath) && isEmpty(excelPath)
                    Material.background: Material.Teal
                    Layout.alignment: "Qt::AlignHCenter"
                }
            }
        }
    }

    FileDialog {
        id: excelFileDialog
        title: qsTr("Sélectionner un fichier excel")
        nameFilters: [ "Fichier Excel (*.xlt *.xlsx *.xlsm *.xltx *.xltm)"]
        onAccepted: {
            statusText.text = "Fichier prêt"
            statusText.color = Material.color(Material.Indigo)
            excelPath = excelFileDialog.currentFile
            appBackend.set_excel_path(excelFileDialog.currentFile)
        }
        onRejected: {
            statusText.text = "Veuillez selectionner un fichier"
            statusText.color = Material.color(Material.Red)
        }
    }

    Connections {
        target: appBackend

        function onSignalLoading(isLoading){
            loading = isLoading
        }

        function onSignalState(state, type){
            var color = Material.color(Material.Indigo)
            if(type == "ERROR"){
                color = Material.color(Material.Red)
            } else if (type == "SUCCESS"){
                color = Material.color(Material.Green)
            }
            statusText.text = state
            statusText.color = color
        }

        function onSignalTemplateUrl(url){
            templateUrl = url
        }

        function onSignalReportPath(path){
            reportPath = path
        }

        function onSignalReset(){
            receiptSelector.currentIndex = -1
            excelPath = ""
        }
    }
}