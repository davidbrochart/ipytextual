# ipytextual

Jupyter Textual-based Widget

## Installation

You can install `ipytextual` using `pip`:

```bash
pip install ipytextual
```

## Development Installation

Create a development environment:

```bash
micromamba create -n ipytextual
micromamba activate ipytextual
micromamba install -c conda-forge python nodejs
pip install jupyterlab
npm install
```

Install the Python package and build the TypeScript package.
```bash
pip install -e .
node_modules/.bin/esbuild --bundle --format=esm --outdir=ipytextual/static src/index.ts
```
