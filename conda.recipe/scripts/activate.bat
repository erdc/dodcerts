@echo off

REM Store existing REQUESTS_CA_BUNDLE env var and set to dodcerts ca bundle path

if defined REQUESTS_CA_BUNDLE (
    set "_CONDA_SET_REQUESTS_CA_BUNDLE=%REQUESTS_CA_BUNDLE%"
)
set "REQUESTS_CA_BUNDLE=%SP_DIR%\dodcerts\dod-ca-certs.pem"