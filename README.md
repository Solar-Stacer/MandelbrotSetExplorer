# How to Use

* This program allows viewing of the Mandelbrot Set plotted on a complex plain. The Mandelbrot set is a
  two-dimensional set. It is defined in the complex plane as the complex numbers c for which the function f(z) =
  z^2 + c does not diverge to infinity when iterated starting at z = 0. In other words, it is the set of for which the
  sequence f(0), f(f(0)), f(f(f(0))), and so on, remains bounded in absolute value.
* **W, A (or Left Arrow), S, D (or Right Arrow)** to move up, left, down, right.
* **Up Arrow** to zoom in and **Down Arrow** to zoom out.
* **Escape** to reset to 0, 0.
* **Ctrl + S** to save a PNG.
* **Ctrl + P** to change location and zoom by input.
* **Ctrl + H** to open this How to Use dialog.
* **Ctrl + A** to open the About dialog.

# For developers

All the image calculations and data handling is done in a shared library compiled from C source `Mandelbrot.c`. 
`Mandelbrot.c` uses OpenMP for multithreading. To compile the source using GCC, use the following commands, 
choosing the one that pertains to your OS (`.so` for Linux and `.dll` for Windows).

For Windows:

```gcc -shared -O3 -fopenmp -march=native -static -o bin/Mandelbrot.dll Mandelbrot.c```

For Linux:

```gcc -shared -O3 -fopenmp -march=native -static -o bin/Mandelbrot.so Mandelbrot.c```