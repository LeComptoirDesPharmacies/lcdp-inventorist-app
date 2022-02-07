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
            RowLayout {
                id: rowLayout
                anchors.fill: parent
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
                        onClicked: loginBackend.login(loginField.text, passwordField.text)
                    }

                    Label {
                        id: loginState
                        text: qsTr("")
                        color: Material.color(Material.Indigo)
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: loginButton.bottom
                        anchors.topMargin: 15
                    }

                    ProgressBar {
                       id: loader
                       indeterminate: true
                       anchors.horizontalCenter: parent.horizontalCenter
                       anchors.top: loginState.bottom
                       anchors.topMargin: 15
                       visible: false
                    }

                }
            }
        }
    }
    
    Connections {
        target: loginBackend

        function onSignalLoading(isLoading){
            loginButton.enabled = !isLoading
            loader.visible = isLoading
        }

        function onSignalConnected(isConnected) {
            if(isConnected){
                var component = Qt.createComponent("app.qml")
                var window = component.createObject()
                window.show()
                visible = false
            }
        }

        function onSignalLoginState(state, isError){
            loginState.text = state
            loginState.color = isError ? Material.color(Material.Red) : Material.color(Material.Indigo)
        }
    }
}