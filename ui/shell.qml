pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

ShellRoot {
    id: root
    property var frame: ({visible: false})
    Socket {
        id: stream
        path: Quickshell.env("FRUITFLY_SOCKET")
        connected: true
        onConnectedChanged: {
            if (connected) { write('{"command":"subscribe"}\n'); flush(); }
            else root.frame = {visible: false};
        }
        parser: SplitParser {
            onRead: data => {
                try { root.frame = JSON.parse(data); }
                catch (error) { root.frame = {visible: false}; }
            }
        }
    }
    Variants {
        model: Quickshell.screens
        PanelWindow {
            id: panel
            required property var modelData
            screen: modelData
            visible: root.frame.visible === true && root.frame.monitor === modelData.name
            implicitWidth: 64
            implicitHeight: 64
            anchors { left: true; top: true }
            margins.left: Math.max(0, (root.frame.localX || 32) - 32)
            margins.top: Math.max(0, (root.frame.localY || 32) - 32)
            color: "transparent"
            exclusionMode: ExclusionMode.Ignore
            WlrLayershell.layer: WlrLayer.Overlay
            WlrLayershell.namespace: "fruitfly"
            WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
            mask: Region {}
            Sprite {
                anchors.fill: parent
                frame: root.frame
                assetsPath: Quickshell.env("FRUITFLY_ASSETS")
                onRendered: {
                    if (stream.connected) {
                        stream.write('{"command":"rendered"}\n'); stream.flush();
                    }
                }
            }
        }
    }
}
