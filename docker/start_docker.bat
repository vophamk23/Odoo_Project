@echo off
chcp 65001 > nul
echo ======================================================================
echo           STARTING PHASE 3 DEDICATED ODOO 19 DOCKER CONTAINER         
echo ======================================================================
echo.
cd /d "%~dp0"
docker compose up -d

echo.
echo ======================================================================
echo Container started on http://localhost:8070
echo Database: gatekeeper_phase3_db
echo ======================================================================
pause
