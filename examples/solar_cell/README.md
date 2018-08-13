# Solar cell example

Note: Only photogeneration works, but the carriers are not taken into account yet.

The photogeneration is done in file `solar.py` in function `beer_lambert_model()`

## Running the example

You need to have devsim already installed. Instructions [here](https://devsim.net/installation.html#sec-installation).

Instructions assume you are going to install it as **root**. If you don't want to use the root account you can link the resulting executable to your `~/bin/` directory:

```bash
ln -s ~/DevSim/devsim/linux_x86_64_release/src/main/devsim_py3 ~/bin/devsim

```

Next thing you need is to create a symlink to the python_packages directory:

```bash
cd ~/DevSim/devsim/examples/solar_cell/
ln -s ../../python_packages/ python_packages
```

Now that you have the symlinks created and the the `devsim` executable on your `$PATH` you can simply run the example through devsim command:

```bash
devsim solar_2d.py
```

There's also a small bash script that does the symlink to `python_packages` for you:

```bash
# This path is an example.
cd ~/DevSim/devsim/examples/solar_cell/
./run.sh
```

Note that you still have to create the symlink for the devsim interpreter (or install as root).
