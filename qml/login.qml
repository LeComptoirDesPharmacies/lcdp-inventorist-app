import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material 2.15

ApplicationWindow {
    id: loginWindow
    title: qsTr("Connexion")
    width: 400
    height: 580
    visible: true
    flags: Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.CustomizeWindowHint | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint

    Material.theme: Material.Light
    Material.accent: '#3AB872'


    function isEmpty(str) {
        return str == ""
    }

    StackView {
        anchors.fill: parent
        initialItem: Page {
            header: Label {
                id: header
                text: qsTr("Connexion")
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
            footer: Pane {
                id: footer
                ColumnLayout {
                    id: footerColumn
                    anchors.fill: parent
                    Label {
                        id: newVersion
                        Layout.fillWidth: true
                        text: qsTr(newVersionAvailable)
                        color: '#FF0000'
                        font.pointSize: 18
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                    }
                    Text {
                        id: link
                        Layout.fillWidth: true
                        text: '<html><style type="text/css"></style><a href="' + newVersionUrl + '">Cliquez ici pour télécharger la nouvelle version</a></html>'
                        onLinkActivated: Qt.openUrlExternally(newVersionUrl)
                        font.pointSize: 18
                        horizontalAlignment: Text.AlignHCenter
                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.NoButton
                            cursorShape: Qt.PointingHandCursor
                        }
                        visible: !isEmpty(newVersionAvailable)
                    }
                    Label {
                        id: currentVersion
                        Layout.fillWidth: true
                        text: qsTr(version)
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
            RowLayout {
                id: rowLayout
                anchors.fill: parent
                focus: true
                Keys.onPressed: (event) => {
                    if (event.key === Qt.Key_Return) {
                        loginButton.clicked()
                    }
                }
                Pane {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Image {
                        id: logo
                        y: 50
                        height: 100
                        width: 100
                        source: "../images/logo.png"
                        anchors.horizontalCenter: parent.horizontalCenter
                        verticalAlignment: Image.AlignVCenter
                        horizontalAlignment: Image.AlignVCenter
                    }

                    TextField {
                        id: loginField
                        width: 300
                        text: qsTr("")
                        selectByMouse: true
                        placeholderText: qsTr("Email")
                        verticalAlignment: Text.AlignVCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: logo.bottom
                        anchors.topMargin: 60
                        focus: true
                    }

                    TextField {
                        id: passwordField
                        width: 300
                        selectByMouse: true
                        placeholderText: qsTr("Mot de passe")
                        echoMode: TextInput.Password
                        verticalAlignment: Text.AlignVCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: loginField.bottom
                        anchors.topMargin: 10
                    }

                    Button {
                        id: loginButton
                        text: qsTr("Se connecter")
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: passwordField.bottom
                        anchors.topMargin: 15
                        enabled: !isEmpty(passwordField.text) && !isEmpty(loginField.text)
                        onClicked: loginBackend.login(loginField.text, passwordField.text)
                    }

                    ProgressBar {
                        id: loader
                        indeterminate: true
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: loginButton.bottom
                        anchors.topMargin: 15
                        visible: false
                    }

                    Label {
                        id: loginState
                        text: qsTr("")
                        color: Material.color(Material.Indigo)
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: loader.bottom
                        anchors.topMargin: 15
                    }

                }
            }
        }
    }

    Connections {
        target: loginBackend

        function onSignalLoading(isLoading) {
            loginButton.enabled = !isLoading
            loader.visible = isLoading
        }

        function onSignalConnected(isConnected) {
            if (isConnected) {
                var component = Qt.createComponent("app.qml")
                var window = component.createObject()
                window.show()
                visible = false
            }
        }

        function onSignalState(state, type) {
            var color = Material.color(Material.Indigo)
            if (type == "ERROR") {
                color = Material.color(Material.Red)
            } else if (type == "SUCCESS") {
                color = Material.color(Material.Green)
            }
            loginState.text = state
            loginState.color = color
        }
    }
}