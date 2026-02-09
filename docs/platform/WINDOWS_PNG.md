# Windows PNG Export

`paperfig` uses `cairosvg` for PNG export, which requires Cairo system libraries.

When PNG export is skipped, run:

```bash
paperfig doctor --fix png
```

## Option 1: MSYS2 UCRT64
1. Install MSYS2:

```powershell
winget install MSYS2.MSYS2
```

2. Open `C:\msys64\ucrt64.exe` and run:

```bash
pacman -Syu
pacman -S --needed mingw-w64-ucrt-x86_64-cairo mingw-w64-ucrt-x86_64-pango mingw-w64-ucrt-x86_64-gdk-pixbuf2
```

3. Add `C:\msys64\ucrt64\bin` to your Windows `PATH`.

4. Verify:

```bash
paperfig doctor --fix png --verify
paperfig doctor
```

## Option 2: Conda-Forge Environment
1. Create env with Cairo stack:

```bash
conda create -n paperfig-png python=3.10 cairosvg cairo pango gdk-pixbuf -c conda-forge
conda activate paperfig-png
```

2. Verify:

```bash
paperfig doctor --fix png --verify
paperfig doctor
```

## Expected Result
`paperfig doctor` should show `python_module:cairosvg` as `ok`.

