# fileclicker

Generate an application that allows you to click filenames, which are picked up by scanning input text file.

A slightly similar tool is `python -m http.server`, which serves a web page including links to files in local directories.

## CLI

```sh
  fileclicker [-p PATTERN|-c COMMAND|-n|-x] <file>...
```

Launch a GUI application that displays text in the argument files, after convert each filename written in text into a clickable button.
When a button is pressed, the filename is printed to standard output. With the option `-c`, you can execute the specified command for the filename.

### Options

```sh
  -p PATTERN        Pattern to filter / capture files.
  -c COMMAND        Command line for the clicked file. `{0}` is argument.
  -n --dry-run      Print commands without running.
```

### Modes

```sh
  -x --check        Check mode. Select files with check box.
  -M --markdown     Markdown mode. Output markdown text.
  -H --html         HTML mode. Output html text.
```
