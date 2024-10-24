import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs
import Qt.labs.qmlmodels

ApplicationWindow {
    title: qsTr("Le Comptoir Des Pharmacies - Gestionnaire d'inventaire")
    visible: true
    minimumWidth: 1350
    minimumHeight: 875

    Material.theme: Material.Light
    Material.accent: '#3AB872'
    property string excelPath: ""
    property string templateUrl: ""
    property bool loading: false
    property bool canClean: false

    function isEmpty(str){
        return str === ""
    }

    StackView {
        anchors.fill: parent

        initialItem: Page {
            id: page

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

            Label {
                id: connexionErrorText
                visible: false
                width: pageView.width
                topPadding: 100
                bottomPadding: 100
                font.pixelSize: 22
                text: qsTr("Erreur de connexion au service Smuggler")
                color: Material.color(Material.Red)
                horizontalAlignment: Text.AlignHCenter
            }

            footer: Label {
                id: footer
                text: qsTr(version)
                leftPadding: 10
                horizontalAlignment: Text.AlignHCenter
            }


            ScrollView {
                id: pageView
                visible: false
                anchors.fill: parent



                ColumnLayout {
                    spacing: 6
                    width: pageView.width

                    Pane {
                        id: card
                        Layout.preferredWidth: parent.width * 0.9

                        height: 400
                        Layout.alignment: "Qt::AlignHCenter"

                        anchors.topMargin: 20
                        Material.elevation: 6
                        ColumnLayout {
                            id: colLayout
                            spacing: 5
                            anchors.fill: parent
                            Text {
                                id: chooseText
                                text: qsTr("Choisir le type d'import ?")
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
                                id: templateLayout
                                width: card.width * 0.9
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

                            ColumnLayout {
                                id: actionLayout
                                height: 800
                                Layout.alignment: "Qt::AlignHCenter"
                                Layout.fillWidth: true

                                spacing: 5
                                CheckBox{
                                    id: shouldClean
                                    text: qsTr("Supprimer les autres annonces de cet utilisateur ?")
                                    visible: canClean
                                    Layout.alignment: "Qt::AlignHCenter"
                                    onCheckedChanged : {
                                        appBackend.should_clean = checked
                                    }
                                }
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
                                    width: parent.width
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
                                    font.pointSize: 12
                                    Layout.alignment: "Qt::AlignHCenter"
                                    MouseArea{
                                        anchors.fill: parent
                                        onClicked:  statusDetails.text ? statusPane.shown = !statusPane.shown : undefined
                                        cursorShape: statusDetails.text ? Qt.PointingHandCursor : undefined
                                    }
                                }
                                Pane {
                                    id: statusPane
                                    Layout.fillWidth: true

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
                                            id: statusDetails
                                            width: parent.width
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
                    Pane {
                        Layout.preferredWidth: parent.width * 0.9
                        Layout.preferredHeight: 400
                        Layout.alignment: "Qt::AlignHCenter"
                        Material.elevation: 6

                        ColumnLayout {
                            id: columnLayout
                            anchors.fill: parent
                            anchors.horizontalCenter: parent.horizontalCenter


                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                HorizontalHeaderView {
                                    id: horizontalHeader
                                    syncView: tableView
                                    model: ["ID", "Date création", "Type d'import", "Tags", "État", "Progression", "Action"]
                                    clip: true
                                    boundsBehavior: Flickable.StopAtBounds

                                    delegate: Rectangle {

                                        implicitHeight: 40
                                        color: "transparent"
                                        border.width: 1
                                        border.color: "lightgray"

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData
                                            font.bold: true
                                        }
                                    }


                                }

                                TableView {
                                    id: tableView
                                    anchors.left: parent.left
                                    anchors.top: horizontalHeader.bottom
                                    anchors.right: parent.right
                                    anchors.bottom: parent.bottom
                                    boundsBehavior: Flickable.StopAtBounds

                                    columnWidthProvider: function (column) {
                                        switch(column) {
                                            case 2: // type
                                                return (width / 7) - 40;
                                            case 3: // tags
                                                return (width / 7) + 120
                                            case 5: // percent
                                                return (width / 7) - 80;
                                            default:
                                                return width / 7
                                        }
                                    }
                                    model: TableModel {
                                        id: tableModel
                                        TableModelColumn {
                                            display: "id"
                                        }
                                        TableModelColumn {
                                            display: "created_at"
                                        }
                                        TableModelColumn {
                                            display: "type"
                                        }
                                        TableModelColumn {
                                            display: "tags"
                                        }
                                        TableModelColumn {
                                            display: "status"
                                        }
                                        TableModelColumn {
                                            display: "percent"
                                        }
                                        TableModelColumn {
                                            display: "action"
                                        }
                                    }


                                    delegate: DelegateChooser {
                                        DelegateChoice {
                                            column: 3 // Colonne "tags"

                                            delegate: Rectangle {
                                                implicitHeight: 50
                                                border.width: 1
                                                border.color: "lightgray"
                                                color: row % 2 === 0 ? "gainsboro" : "white"

                                                Text {
                                                    anchors.fill: parent
                                                    anchors.margins: 5
                                                    horizontalAlignment: Text.AlignLeft
                                                    verticalAlignment: Text.AlignVCenter
                                                    text: model.display
                                                    elide: Text.ElideRight
                                                    wrapMode: Text.Wrap
                                                }

                                                 ToolTip {
                                                    visible: mouseArea.containsMouse
                                                    text: model.display
                                                }

                                                MouseArea {
                                                    id: mouseArea
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                }

                                            }
                                        }

                                        DelegateChoice {
                                            column: 4 // Colonne "status"
                                            delegate: Rectangle {
                                                implicitHeight: 50
                                                border.width: 1
                                                border.color: "lightgray"
                                                color: row % 2 === 0 ? "gainsboro" : "white"
                                                Text {
                                                    text: model.display
                                                    anchors.centerIn: parent
                                                    color: {
                                                        const lowerStatus = model.display.toLowerCase();
                                                        if (lowerStatus.includes("erreur")) return "red";
                                                        else if (lowerStatus.includes("terminé")) return "green";
                                                        else return "black";
                                                    }
                                                }
                                            }
                                        }
                                        DelegateChoice {
                                            column: 5 // Colonne "percent"
                                            delegate: Rectangle {
                                                implicitHeight: 50
                                                border.width: 1
                                                border.color: "lightgray"
                                                color: row % 2 === 0 ? "gainsboro" : "white"

                                                ProgressBar {
                                                    anchors.centerIn: parent
                                                    width: parent.width * 0.8
                                                    height: 20
                                                    from: 0
                                                    to: 100
                                                    value: model.display

                                                    Text {
                                                        anchors.centerIn: parent
                                                        anchors.verticalCenterOffset: 15
                                                        text: model.display + " %"
                                                        color: "black"
                                                        z: 1
                                                    }
                                                }
                                            }
                                        }
                                        DelegateChoice {
                                            column: 6
                                            delegate: Rectangle {
                                                implicitHeight: 50
                                                border.width: 1
                                                border.color: "lightgray"
                                                color: row % 2 === 0 ? "gainsboro" : "white"
                                                Button {
                                                    flat: true
                                                    text: "💾 Télécharger"
                                                    anchors.centerIn: parent
                                                    visible: tableModel.rows.length ? (tableModel.rows[row].statusType === "DONE" && tableModel.rows[row].percent >= 100) : false
                                                    onClicked: {
                                                        appBackend.downloadAndOpenFile(tableModel.rows[row].id)
                                                    }
                                                }
                                            }
                                        }
                                        DelegateChoice {
                                            delegate: Rectangle {
                                                implicitHeight: 50
                                                border.width: 1
                                                border.color: "lightgray"
                                                color: row % 2 === 0 ? "gainsboro" : "white"
                                                Text {
                                                    horizontalAlignment: Text.AlignHCenter
                                                    width: parent.width
                                                    text: model.display
                                                    wrapMode: Text.Wrap
                                                    anchors.centerIn: parent
                                                }
                                            }
                                        }
                                    }
                                }

                            }
                        }
                    }
                }

                Binding
                {
                    target: pageView.contentItem
                    property: "boundsBehavior"
                    value: Flickable.StopAtBounds
                }
            }

        }
    }

    Timer {
        interval: 5000 // 5 secondes
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            appBackend.refresh_data()
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

        function onSignalState(state, type, details, canDisable) {
            let color = Material.color(Material.Indigo);
            if (type === "ERROR") {
                color = Material.color(Material.Red)
            } else if (type === "SUCCESS") {
                color = Material.color(Material.Green)
            }
            statusText.text = state
            statusText.color = color
            statusPane.shown = false
            statusDetails.text = details
            statusDetails.color = Material.color(Material.Red)
        }

        function onSignalTemplateUrl(url){
            templateUrl = url
        }

        function onSignalRefreshData(newData){
            console.log("refreshdata", new Date())
            tableModel.clear()
            for (let i = 0; i < newData.length; i++) {
                tableModel.appendRow(newData[i])
            }
        }

        function onSignalCanClean(signalCanClean){
            canClean = signalCanClean
        }

        function onSignalReset(){
            receiptSelector.currentIndex = -1
            excelPath = ""
        }

        function onSignalConnexionStatus(isSuccess) {
            connexionErrorText.visible = !isSuccess
            pageView.visible = isSuccess
        }
    }
}
