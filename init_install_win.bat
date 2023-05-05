
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
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

@REM install odbc driver
reg query "HKLM\SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 18 for SQL Server" > nul
if %errorlevel% neq 0 (
    curl -L https://go.microsoft.com/fwlink/?linkid=2223270 -o odbc.msi
    ".\odbc.msi"
    del ".\odbc.msi"
)

@REM install nvidia driver