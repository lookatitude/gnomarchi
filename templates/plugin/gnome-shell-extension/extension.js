import GObject from 'gi://GObject';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

const Button = GObject.registerClass(
class Button extends PanelMenu.Button {
    _init() {
        super._init(0.0, 'PLUGIN_ID');
        this.add_child(new St.Label({ text: 'G', y_align: 2 }));
    }
});

export default class Extension {
    enable() {
        this._button = new Button();
        Main.panel.addToStatusArea('PLUGIN_ID', this._button);
    }
    disable() {
        this._button?.destroy();
        this._button = null;
    }
}
