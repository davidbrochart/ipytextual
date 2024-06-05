# Copyright (c) David Brochart.
# Distributed under the terms of the Modified BSD License.

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from anywidget import AnyWidget
from traitlets import Bool, Bytes, Int, Unicode

from .driver import SIZE


bundler_output_dir = Path(__file__).parent / "static"


class Widget(AnyWidget):
    _esm = bundler_output_dir / "index.js"

    _data_from_textual = Bytes().tag(sync=True)
    _data_to_textual = Unicode().tag(sync=True)
    _cols = Int(80).tag(sync=True)
    _rows = Int(24).tag(sync=True)
    _font_size = Int(20).tag(sync=True)
    _ready = Bool().tag(sync=True)

    def __init__(
        self,
        app,
        cols: int | None = None,
        rows: int | None = None,
        font_size: int | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._app = app
        if cols is not None:
            self._cols = cols
            SIZE[0] = cols
        if rows is not None:
            self._rows = rows
            SIZE[1] = rows
        if font_size is not None:
            self._font_size = font_size
        self._data_from_textual_queue = asyncio.Queue()
        self._data_to_textual_queue = asyncio.Queue()
        self._ready_event = asyncio.Event()
        self._tasks = [
            asyncio.create_task(self._run()),
            asyncio.create_task(self._send_data()),
            asyncio.create_task(self._recv_data()),
        ]
        self.observe(self._observe_cols, names=["_cols"])
        self.observe(self._observe_rows, names=["_rows"])
        self.observe(self._observe_ready, names=["_ready"])
        self.observe(self._observe_data_to_textual, names=["_data_to_textual"])

    def _observe_data_to_textual(self, change):
        data = bytes(change["new"], "utf8")
        self._data_to_textual_queue.put_nowait(data)

    async def _send_data(self):
        await self._ready_event.wait()
        while True:
            data = await self._data_from_textual_queue.get()
            self._data_from_textual = data

    async def _recv_data(self):
        while True:
            data = await self._data_to_textual_queue.get()
            packet_type = b"D"
            packet = b"%s%s%s" % (packet_type, len(data).to_bytes(4, "big"), data)
            self._app._driver._stdin_queue.put_nowait(packet)

    def _observe_ready(self, change):
        self._ready_event.set()

    def _observe_cols(self, change):
        SIZE[0] = change["new"]

    def _observe_rows(self, change):
        SIZE[1] = change["new"]

    async def _run(self):
        self._tasks.append(asyncio.create_task(self._app.run_async()))
        while True:
            if self._app._driver is not None:
                break
            await asyncio.sleep(0)

        for _ in range(10):
            line = []
            while True:
                data = await self._app._driver._stdout_queue.get()
                line.append(data)
                if data[-1] == 10:  # "\n"
                    break
            line = b"".join(line)
            if not line:
                break
            if line == b"__GANGLION__\n":
                ready = True
                break
        if ready:
            META = 77  # b"M"
            DATA = 68  # b"D"
            while True:
                data = await self._app._driver._stdout_queue.get()
                type_bytes = data[0]
                size_bytes = data[1:5]
                size = int.from_bytes(size_bytes, "big")
                data = data[5:5 + size]
                if type_bytes == DATA:
                    self._data_from_textual_queue.put_nowait(data)
                elif type_bytes == META:
                    meta_data = json.loads(data)
                    #if meta_data.get("type") == "exit":
                    #    await self.send_meta({"type": "exit"})
                    #else:
                    #    await on_meta(json.loads(data))
