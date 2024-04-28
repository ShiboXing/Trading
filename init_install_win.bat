@REM install gcc and boost
@REM where g++ > nul 2>&1
@REM if %errorlevel% neq 0 (
@REM     echo g++ is not installed, installing MSYS2...
@REM     curl https://github.com/msys2/msys2-installer/releases/download/2023-03-18/msys2-x86_64-20230318.exe -o msy32_installer.exe
@REM     msy32_installer.exe
@REM     curl https://boostorg.jfrog.io/artifactory/main/release/1.82.0/source/boost_1_82_0.zip -o boost_installer.zip
@REM )


@REM install python packages
pip install ipdb ^
    ipython ^
    black ^
    yfinance ^
    numpy ^
    pandas ^
    matplotlib ^
    sqlalchemy ^
    pyodbc ^
    jupyterlab ^
    notebook ^
    yahooquery ^
    tushare 

@REM install pytorch
pip3 install torch

@REM NEED TO INSTALL MSSQL SERVER FIRST!!!

@REM install odbc driver
reg query "HKLM\SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 18 for SQL Server" > nul
if %errorlevel% neq 0 (
    curl https://go.microsoft.com/fwlink/?linkid=2223270 -o odbc.msi
    ".\odbc.msi"
    del ".\odbc.msi"
)

@REM install rumble
rm -rf build/ rumble.egg-info
pip install .