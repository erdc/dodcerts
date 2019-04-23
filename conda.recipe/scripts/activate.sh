#!/bin/bash

# Store existing REQUESTS_CA_BUNDLE env var and set to dodcerts ca bundle path

if [[ -n "$REQUESTS_CA_BUNDLE" ]]; then
    export _CONDA_SET_REQUESTS_CA_BUNDLE=$REQUESTS_CA_BUNDLE
fi

export REQUESTS_CA_BUNDLE=$SP_DIR/dodcerts/dod-ca-certs.pem
