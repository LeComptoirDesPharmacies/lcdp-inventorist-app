import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material 2.15

ApplicationWindow {
    id: loginWindow
    title: qsTr("Connexion")
    width: 400
    height: 620
    visible: true

    Material.theme: Material.Light
    Material.accent: '#3AB872'


    function isEmpty(str) {
        return str === ""
    }

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: loginPage
    }

    Page {
        id: loginPage
        header: ColumnLayout {
            id: headerColumn
            Label {
                id: newVersion
                Layout.fillWidth: true
                text: qsTr(newVersionAvailable)
                color: '#FF0000'
                font.pointSize: 18
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                visible: !isEmpty(newVersionAvailable)
                wrapMode: Text.WordWrap
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
                wrapMode: Text.WordWrap
            }
            Label {
                id: header
                Layout.fillWidth: true
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
                visible: isEmpty(newVersionAvailable)
            }
        }
        footer: Label {
            id: footer
            text: qsTr(version)
            leftPadding: 10
            horizontalAlignment: Text.AlignHCenter
        }

         ScrollView {
            id: pageView
            anchors.fill: parent

            RowLayout {
                id: rowLayout
                width: pageView.width
                focus: true
                visible: isEmpty(newVersionAvailable)
                Keys.onPressed: (event) => {
                    if (event.key === Qt.Key_Return) {
                        loginButton.clicked()
                    }
                }
                Pane {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ColumnLayout {
                        width: parent.width
                        spacing: 15

                        Image {
                            id: logo
                            Layout.topMargin: 30
                            Layout.bottomMargin: 50
                            Layout.preferredWidth: 100
                            Layout.preferredHeight: 100
                            source: "../images/logo.png"
                            Layout.alignment: "Qt::AlignHCenter"
                        }

                        TextField {
                            id: loginField
                            Layout.preferredWidth: 300
                            text: qsTr("seller_buyer@mail.test")
                            selectByMouse: true
                            placeholderText: qsTr("Email")
                            focus: true
                            Layout.alignment: "Qt::AlignHCenter"
                        }

                        TextField {
                            id: passwordField
                            Layout.preferredWidth: 300
                            text: qsTr("")
                            selectByMouse: true
                            placeholderText: qsTr("Mot de passe")
                            echoMode: TextInput.Password
                            Layout.alignment: "Qt::AlignHCenter"
                        }

                        Button {
                            id: loginButton
                            text: qsTr("Se connecter")
                            Layout.topMargin: 5
                            enabled: !isEmpty(passwordField.text) && !isEmpty(loginField.text)
                            onClicked: loginBackend.login(loginField.text, passwordField.text)
                            Layout.alignment: "Qt::AlignHCenter"
                        }

                        ProgressBar {
                            id: loader
                            indeterminate: true
                            Layout.topMargin: 5
                            visible: false
                            Layout.alignment: "Qt::AlignHCenter"
                        }

                        Label {
                            id: loginState
                            text: qsTr("")
                            color: Material.color(Material.Indigo)
                            Layout.alignment: "Qt::AlignHCenter"
                            MouseArea{
                                anchors.fill: parent
                                onClicked:  loginDetails.text ? loginPane.shown = !loginPane.shown : undefined
                                cursorShape: loginDetails.text ? Qt.PointingHandCursor : undefined
                            }
                        }

                        Pane {
                            id: loginPane
                            Layout.preferredWidth: parent.width

                            // ## relevant part ##
                            property bool shown: false
                            visible: height > 0
                            height: shown ? implicitHeight : 0
                            Behavior on height {
                                NumberAnimation {
                                    easing.type: Easing.InOutQuad
                                }
                            }
                            clip: true
                            // ## relevant part ##

                            background: Rectangle {
                                color: "#d0d0d0"
                            }

                            Column {
                                anchors.right: parent.right
                                anchors.left: parent.left

                                TextEdit  {
                                    width: parent.width
                                    id: loginDetails
                                    text: qsTr("")
                                    font.pointSize: 12
                                    Layout.alignment: "Qt::AlignHCenter"
                                    wrapMode: Text.WordWrap
                                    readOnly: true
                                    selectByMouse: true
                                }
                            }
                        }
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
                stackView.push("app.qml")
                visible = false
            }
        }

        function onSignalState(state, type, details) {
            var color = Material.color(Material.Indigo)
            if (type == "ERROR") {
                color = Material.color(Material.Red)
            } else if (type == "SUCCESS") {
                color = Material.color(Material.Green)
            }
            loginState.text = state
            loginState.color = color
            loginPane.shown = false
            loginDetails.text = details
            loginDetails.color = Material.color(Material.Red)
        }
    }
}
