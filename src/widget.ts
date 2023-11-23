// Copyright (c) David Brochart
// Distributed under the terms of the Modified BSD License.

import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';

export function render({ model, el }) {
  const cols = model.get('_cols');
  const rows = model.get('_rows');
  const terminal = new Terminal({cols, rows});
  const fitAddon = new FitAddon();
  terminal.loadAddon(fitAddon);
  terminal.open(el);
  fitAddon.fit();

  new Widget(model, terminal);
}


class Widget {
  constructor(model, terminal) {
    this.model = model;
    this.terminal = terminal;

    terminal.onData(this.send_data);
    terminal.onResize(this.resize);

    model.on('change:_data_from_textual', this.write);
    model.set('_cols', terminal.cols);
    model.set('_rows', terminal.rows);
    model.set('_ready', true);
    model.save_changes();
  }

  resize = (event) => {
    this.model.set('_cols', event.cols);
    this.model.set('_rows', event.rows);
    this.model.save_changes();
  }

  write = () => {
    const data = this.model.get('_data_from_textual');
    const array = new Uint8Array(data.buffer);
    this.terminal.write(array);
  }

  send_data = (data) => {
    this.model.set('_data_to_textual', data);
    this.model.save_changes();
  }

  terminal: Terminal;
}
