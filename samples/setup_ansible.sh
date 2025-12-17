#!/usr/bin/env bash
SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PYTHON_INTERPRETER=${PYTHON_INTERPRETER}
VENV_PATH=${VENV_PATH:-$SCRIPT_DIR/../.linuxenv}

function setPythonInterpreter() {
    latest_version=""
    latest_binary=""

    # Loop through each directory in PATH
    IFS=':' read -ra dirs <<<"$PATH"
    for dir in "${dirs[@]}"; do
        # Look for python3* binaries
        for bin in "$dir"/python3*; do
            [ -x "$bin" ] || continue
            [[ "$bin" =~ python3([.][0-9]+)?$ ]] || continue

            version=$("$bin" -V 2>&1 | awk '{print $2}')
            if [ -z "$latest_version" ] || [ "$(printf '%s\n' "$latest_version" "$version" | sort -V | tail -n1)" = "$version" ]; then
                latest_version="$version"
                latest_binary="$bin"
            fi
        done
    done

    if [ -n "$latest_binary" ]; then
        echo "-> Latest Python binary: $latest_binary"
        echo "-> Version: $latest_version"
        PYTHON_INTERPRETER=$latest_binary
    else
        echo "No Python 3 binaries found in PATH."
        exit 1
    fi
}

if [[ "$PYTHON_INTERPRETER" == "" ]]; then
    setPythonInterpreter
fi

if [[ ! -f $VENV_PATH/bin/activate ]]; then
    echo "-> Create Python virtual environment at $VENV_PATH"
    $PYTHON_INTERPRETER -m venv $VENV_PATH
fi
. $VENV_PATH/bin/activate
echo "-> Updating PiP and installing dependencies using $VENV_PATH"
pip install -U pip
pip install ansible-core ansible-dev-tools molecule-plugins[vagrant]
pip install -r $SCRIPT_DIR/../requirements.txt

COLLECTIONS_HAXOROF_DIR="$HOME/.ansible/collections/ansible_collections/haxorof"
COLLECTIONS_SYMLINK="$COLLECTIONS_HAXOROF_DIR/sonatype_nexus"
if [[ -L $COLLECTIONS_SYMLINK ]]; then
    echo "Symbolic link already exists:"
    ls -l $COLLECTIONS_SYMLINK
else
    mkdir -p $COLLECTIONS_HAXOROF_DIR
    cd ..
    ln -s $(pwd) $COLLECTIONS_SYMLINK
    cd -
fi
echo "Python virtual environment at $VENV_PATH"
echo "Done!"
