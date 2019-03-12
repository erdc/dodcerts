#!/usr/bin/env sh

set -ev

# execute python script to recreate bundle, compare, and overwrite if new
if python ./update/update.py ; then
    echo "push new bundle"
    # set up git
    git config --global user.email "travis@travis-ci.org"
    git config --global user.name "Travis CI"

    # commit new bundle
    git checkout -b new_bundle
    git add ./dodcerts/dod-ca-certs.pem
    git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"

    # upload
    git remote add origin_bundle https://github.com/erdc/dodcerts.git > /dev/null 2>&1
    git push --quiet --set-upstream origin_bundle new_bundle
fi
