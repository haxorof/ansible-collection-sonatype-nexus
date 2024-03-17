#!/usr/bin/env bash
SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ ! -d $SCRIPT_DIR/../.linuxenv ]]; then
    python3 -m venv $SCRIPT_DIR/../.linuxenv
fi
. $SCRIPT_DIR/../.linuxenv/bin/activate
pip install -U pip
pip install ansible-core
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
echo "Done!"