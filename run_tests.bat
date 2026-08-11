@echo off
title Gate Keeper API Test Runner
echo ===================================================
echo   Starting Gate Keeper API Excel Test Suite...
echo ===================================================
cd /d %~dp0
set PYTHONIOENCODING=utf-8
python tests/run_excel_tests.py
echo.
echo ===================================================
echo   Tests Completed!
echo   Opening results file...
echo ===================================================
start tests\api_test_results.xlsx
pause
