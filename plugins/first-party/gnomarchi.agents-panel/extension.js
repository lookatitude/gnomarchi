import GObject from 'gi://GObject';
import St from 'gi://St';
import Gio from 'gi://Gio';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

const AgentsButton = GObject.registerClass(
class AgentsButton extends PanelMenu.Button {
    _init() {
        super._init(0.0, 'gnomarchi Agents');
        this.add_child(new St.Label({
            text: '󱚣',
            y_align: 2,
            style_class: 'system-status-icon',
        }));
        this.connect('button-press-event', (_a, event) => {
            const btn = event.get_button();
            if (btn === 1)
                this._spawn(['gnomarchi', 'agent', 'window']);
            else if (btn === 3)
                this._spawn(['gnomarchi', 'agent', 'launch']);
            return true;
        });
    }

    _spawn(argv) {
        try {
            Gio.Subprocess.new(argv, Gio.SubprocessFlags.NONE);
        } catch (e) {
            Main.notifyError('gnomarchi', String(e));
        }
    }
});

export default class Extension {
    enable() {
        this._button = new AgentsButton();
        Main.panel.addToStatusArea('gnomarchi-agents', this._button);
    }

    disable() {
        this._button?.destroy();
        this._button = null;
    }
}
