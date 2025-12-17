#!/usr/bin/env bash
BASH_LOCAL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ANSIBLE_HOME=~/.ansible
NAMESPACE_DIR=$ANSIBLE_HOME/collections/ansible_collections/haxorof
COLLECTION_DIR=$NAMESPACE_DIR/sonatype_nexus

# echo "--> Checking namespace directory $NAMESPACE_DIR"
if [[ ! -d $NAMESPACE_DIR ]]; then
  mkdir -p $NAMESPACE_DIR
  echo "--> Created directory $NAMESPACE_DIR"
fi

CREATE_SYMLINK=0
# echo "--> Checking collection symlink $COLLECTION_DIR"
if [[ -d $COLLECTION_DIR ]]; then
  if [[ -h $COLLECTION_DIR ]]; then
    CURRENT_SYMLINK=$(readlink -f $COLLECTION_DIR)
    if [[ $CURRENT_SYMLINK == $BASH_LOCAL_DIR ]]; then
      echo "--> Symlink to collection already exists: $COLLECTION_DIR"
    else
      echo "--> Incorrect symlink pointing to $CURRENT_SYMLINK, recreating!"
      rm $COLLECTION_DIR
      CREATE_SYMLINK=1
    fi
  else
    echo "--> Directory already exists but not symlink at $COLLECTION_DIR, deleting!"
    rm -rf $COLLECTION_DIR
    CREATE_SYMLINK=1
  fi
else
  if [[ -h $COLLECTION_DIR ]]; then
    CURRENT_SYMLINK=$(readlink -f $COLLECTION_DIR)
    if [[ $CURRENT_SYMLINK != $BASH_LOCAL_DIR ]]; then
      echo "--> Incorrect symlink pointing to $CURRENT_SYMLINK, recreating!"
      rm $COLLECTION_DIR
      CREATE_SYMLINK=1
    fi
  fi
  CREATE_SYMLINK=1
fi

if [[ "$CREATE_SYMLINK" == "1" ]]; then
  ln -s $BASH_LOCAL_DIR $COLLECTION_DIR
  echo "--> Created symbolic link $COLLECTION_DIR to $BASH_LOCAL_DIR"
fi

