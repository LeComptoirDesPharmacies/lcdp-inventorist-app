import QtQuick
import QtQuick.Window 2.15
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

    Material.theme: Material.Dark
    Material.accent: Material.LightBlue
    
    RowLayout {
        anchors.fill: parent;
        Pane {
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;
            anchors.horizontalCenter: parent.horizontalCenter
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
        }
    }
    
    Connections {
        target: loginBackend

        property string userName: ""

        function onSignalUserName(name){
            userName = name
        }

        function onSignalLoading(isLoading){
            loginButton.enabled = !isLoading
        }

        function onSignalConnected(isConnected) {
            if(isConnected){
                var component = Qt.createComponent("app.qml")
                var window = component.createObject()
                window.userName = userName
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