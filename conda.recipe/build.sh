#!/bin/bash

# Build

python setup.py install --single-version-externally-managed --record=record.txt

## Add activate/deactivate scripts
#
#ACTIVATE_DIR=$PREFIX/etc/conda/activate.d
#DEACTIVATE_DIR=$PREFIX/etc/conda/deactivate.d
#mkdir -p $ACTIVATE_DIR
#mkdir -p $DEACTIVATE_DIR
#
#cp $RECIPE_DIR/scripts/activate.sh $ACTIVATE_DIR/dodcerts-activate.sh
#cp $RECIPE_DIR/scripts/deactivate.sh $DEACTIVATE_DIR/dodcerts-deactivate.sh