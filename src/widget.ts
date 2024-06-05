// Copyright (c) David Brochart
// Distributed under the terms of the Modified BSD License.

import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebglAddon } from 'xterm-addon-webgl';
import { CanvasAddon } from 'xterm-addon-canvas';
import { Unicode11Addon } from 'xterm-addon-unicode11';

export function render({ model, el }) {
  const cols = model.get('_cols');
  const rows = model.get('_rows');
  const font_size = model.get('_font_size');
  const terminal = new Terminal({
    allowProposedApi: true,
      fontSize: font_size,
      scrollback: 0,
      fontFamily: "'Roboto Mono', Monaco, 'Courier New', monospace",
    cols,
    rows
  });
  const fitAddon = new FitAddon();
  terminal.loadAddon(fitAddon);
  const webglAddon = new WebglAddon();
  terminal.loadAddon(webglAddon);
  const canvasAddon = new CanvasAddon();
  terminal.loadAddon(canvasAddon);
  const unicode11Addon = new Unicode11Addon();
  terminal.loadAddon(unicode11Addon);
  terminal.unicode.activeVersion = "11";
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
