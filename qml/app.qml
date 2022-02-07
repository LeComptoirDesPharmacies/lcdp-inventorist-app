import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs

ApplicationWindow {
    title: qsTr("Le Comptoir Des Pharmacies - Gestionnaire d'inventaire")
    width: 500
    height: 480
    visible: true
    flags: Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.CustomizeWindowHint | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint

    Material.theme: Material.Light
    Material.accent: '#3AB872'

    property string currentState: ""
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
                width: 400
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
                        font.pointSize: 18
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
                        model: [
                            {'text': "Boutique PharmLab", 'value': "PHARMLAB_STORE"}
                        ]
                        onActivated: appBackend.select_receipt(currentValue)
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
                            font.pointSize: 14
                        }
                        Text {
                            id: templateLink
                            text: '<html><style type="text/css"></style><a href="'+templateUrl+'">Template '+receiptSelector.currentText+'</a></html>'
                            onLinkActivated: Qt.openUrlExternally(link)
                            font.pointSize: 14
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
                    text: qsTr("Sélectionner un fichier excel")
                    onClicked: excelFileDialog.visible = true
                    Layout.alignment: "Qt::AlignHCenter"
                    visible: !loading
                }
                Text {
                    id: excelPathText
                    color: '#1E276D'
                    text: excelPath
                    font.pointSize: 12
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
                    color: '#1E276D'
                    text: currentState
                    font.pointSize: 12
                    Layout.alignment: "Qt::AlignHCenter"
                }
                Button {
                    id: openReport
                    Layout.topMargin: 30
                    text: qsTr("Ouvrir le rapport")
                    onClicked: appBackend.open_file(reportPath)
                    visible: !isEmpty(reportPath)
                    Layout.alignment: "Qt::AlignHCenter"
                }
            }
        }
    }

    FileDialog {
        id: excelFileDialog
        title: qsTr("Sélectionner un fichier excel")
        nameFilters: [ "All files (*)"]
        onAccepted: {
            excelPath = excelFileDialog.currentFile
            appBackend.get_excel(excelFileDialog.currentFile)
        }
        onRejected: {
            console.log("Canceled")
        }
    }

    Connections {
        target: appBackend

        function onSignalLoading(isLoading){
            loading = isLoading
        }

        function onSignalChangeState(state){
            currentState = state
        }

        function onSignalTemplateUrl(url){
            templateUrl = url
        }

        function onSignalReportPath(path){
            reportPath = path
        }
    }
}