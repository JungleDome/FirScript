@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto html

if "%1" == "clean" goto clean

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:clean
echo Cleaning build directory...
if exist %BUILDDIR% rmdir /s /q %BUILDDIR%
echo Build directory cleaned.
goto end

:html
echo Building HTML documentation with full rebuild...
if exist %BUILDDIR%\doctrees rmdir /s /q %BUILDDIR%\doctrees
%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%/html -E -a %SPHINXOPTS% %O%
echo HTML documentation built.
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
echo.
echo Additional commands:
echo   clean      - Clean the build directory
echo   html       - Build HTML with full rebuild (no caching)

:end
popd
