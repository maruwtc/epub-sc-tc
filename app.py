import zipfile
import opencc
from pathlib import Path

# Only initialize OpenCC once, or it would be very slow.
converter = opencc.OpenCC(config="s2tw.json")


def convert_epub(epub, output):
    target_filetype = ["htm", "html", "xhtml", "ncx", "opf"]

    try:
        origin = zipfile.ZipFile(epub, mode="r")
    except zipfile.BadZipFile as e:
        print(f"Error: {epub} is not a valid EPUB file. {e}")
        return None
    except Exception as e:
        print(f"Error opening {epub}: {e}")
        return None

    try:
        copy = zipfile.ZipFile(output, mode="w")
    except Exception as e:
        print(f"Error creating output ZIP for {epub}: {e}")
        origin.close()
        return None

    for fn in origin.namelist():
        try:
            info = origin.getinfo(fn)
            extension = Path(fn).suffix[1:]  # Remove leading `.`
            if extension in target_filetype:
                # Decode byte content to string.
                sc_content = origin.read(fn).decode("utf-8")
                tc_content = convert_content(sc_content)
                if extension == "opf":
                    tc_content = tc_content.replace(
                        "<dc:language>zh-CN</dc:language>",
                        "<dc:language>zh-TW</dc:language>",
                    )
                # Encode the converted text back to bytes.
                copy.writestr(
                    s2t(fn),
                    tc_content.encode("utf-8"),
                    compress_type=info.compress_type,
                )
            else:
                # Write non-target files directly.
                copy.writestr(
                    s2t(fn),
                    origin.read(fn),
                    compress_type=info.compress_type,
                )
        except Exception as e:
            print(f"Error processing file '{fn}' in {epub}: {e}")
            continue

    origin.close()
    copy.close()
    return output


def convert_content(content):
    # Process each line through the converter.
    return "\n".join(s2t(line) for line in content.splitlines())


def s2t(text):
    return converter.convert(text)


def convert_directory(directory):
    """
    Convert all EPUB files in the specified directory.
    The output files will be saved in the same directory.
    """
    from io import BytesIO
    import time

    directory_path = Path(directory)
    for epub in directory_path.glob("*.epub"):
        if not epub.suffix == ".epub":
            print(f"Skipping file {epub}, which is not an EPUB document.")
            continue

        try:
            filename = epub.name
            # Determine output file name based on conversion of the original name.
            if filename == s2t(filename):
                output_filename = epub.stem + ".epub"
            else:
                output_filename = s2t(filename)

            # Create the output path in the same directory.
            # Ensure the "tc" directory exists.
            (directory_path / "tc").mkdir(parents=True, exist_ok=True)
            output_path = directory_path / "tc" / output_filename
            print(f"Converting {epub} to {output_path}")
            t = time.time()
            buffer = BytesIO()
            result = convert_epub(epub, buffer)
            if result is None:
                print(f"Skipping {epub} due to errors.")
                continue
            with open(output_path, "wb") as f:
                f.write(buffer.getvalue())
            print(
                f"File {epub} successfully converted. Time elapsed: {round(time.time() - t, 2)}s"
            )
        except Exception as e:
            print(f"Error converting file {epub}: {e}")


if __name__ == "__main__":
    import argparse
    import glob
    import time
    from io import BytesIO

    parser = argparse.ArgumentParser(
        description="Convert simplified Chinese to traditional Chinese in EPUB files."
    )
    parser.add_argument("file", nargs="*", help="EPUB file(s) to convert")
    parser.add_argument(
        "-d", "--directory", help="Directory containing EPUB files to convert"
    )
    args = parser.parse_args()

    # If a directory is provided, convert all EPUBs in that directory.
    if args.directory:
        convert_directory(args.directory)
    # Otherwise, process individual files or glob patterns.
    elif args.file:
        # Support glob patterns (e.g., "*.epub")
        if len(args.file) == 1 and "*" in args.file[0]:
            fn_list = glob.glob(args.file[0])
        else:
            fn_list = args.file

        for fn in fn_list:
            path = Path(fn)
            directory = path.parent.absolute()
            filename = path.name

            if not path.suffix == ".epub":
                print(f"Skipping file {fn}, which is not an EPUB document.")
                continue

            try:
                if filename == s2t(filename):
                    output_fn = path.with_name(path.stem + "-tc.epub")
                else:
                    output_fn = path.with_name(s2t(filename))

                t = time.time()
                print(f"Converting {fn}")
                buffer = BytesIO()
                result = convert_epub(fn, buffer)
                if result is None:
                    print(f"Skipping {fn} due to errors.")
                    continue
                with open(output_fn, "wb") as f:
                    f.write(buffer.getvalue())
                print(
                    f"File {fn} is successfully converted. Time elapsed: {round(time.time() - t, 2)}s"
                )
            except Exception as e:
                print(f"Error converting file {fn}: {e}")
    else:
        print("No EPUB files or directory specified for conversion.")
