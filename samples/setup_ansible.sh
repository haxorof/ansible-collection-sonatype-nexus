#!/usr/bin/env bash
cd ../
if [[ ! -d .linuxenv ]]; then
    python3 -m venv .linuxenv
fi
. .linuxenv/bin/activate
pip install -U pip
pip install ansible-core
pip install -r ./requirements.txt

COLLECTIONS_SYMLINK="$HOME/.ansible/collections/ansible_collections/haxorof/sonatype_nexus"
if [[ -L $COLLECTIONS_SYMLINK ]]; then
    echo "Symbolic link already exists:"
    ls -l $COLLECTIONS_SYMLINK
else
    ln -s $(pwd) $COLLECTIONS_SYMLINK
fi
echo "Done!"