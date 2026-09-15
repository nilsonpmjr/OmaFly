import QtQuick

Item {
    id: sprite
    width: 64
    height: 64
    property var frame: ({})
    property string assetsPath
    signal rendered()
    // An absent mask means exposed; [] deliberately means fully occluded.
    property var pieces: frame.clips !== undefined ? frame.clips :
                         [{x: 0, y: 0, width: 64, height: 64}]
    Repeater {
        model: sprite.pieces
        Item {
            required property var modelData
            x: modelData.x; y: modelData.y
            width: modelData.width; height: modelData.height
            clip: true
            Image {
                x: -parent.x; y: -parent.y
                width: 64; height: 64
                source: "file://" + sprite.assetsPath +
                        (sprite.frame.mode === "flight" ? "/fly-flight-" + (sprite.frame.frame || 0) + ".svg" :
                         sprite.frame.mode === "walk" ? "/fly-walk-" + (sprite.frame.frame || 0) + ".svg" : "/fly.svg")
                sourceSize.width: 64; sourceSize.height: 64
                smooth: false
                mirror: sprite.frame.faceLeft !== true
                cache: true
                onStatusChanged: if (status === Image.Ready) sprite.rendered()
            }
        }
    }
}
