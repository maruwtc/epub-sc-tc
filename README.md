# EPUB Simplified Chinese to Traditional Chinese Converter

This Python script batch-converts EPUB files containing Simplified Chinese text to Traditional Chinese using OpenCC. It operates on individual files or entire directories.

---

## 📦 Features

- Convert `.epub` files from Simplified Chinese to Traditional Chinese.
- Automatically updates language tags (e.g., `zh-CN` ➜ `zh-TW`).
- Preserves original EPUB structure and compression.
- Supports both single file and directory processing.
- Handles file name conversion if it contains Chinese characters.

---

## 🧩 Requirements

- Python 3.7+
- [OpenCC](https://github.com/BYVoid/OpenCC)

Install dependencies:

```bash
pip install opencc-python-reimplemented
```

## ▶️ Usage

Convert a single file:

```bash
python convert_epub.py path/to/book.epub
```

Convert all .epub files in a directory:

```bash
python convert_epub.py -d path/to/folder
```

Glob pattern support:

```bash
python convert_epub.py "*.epub"
```

## 📁 Output
Converted files are saved in the `tc` directory.