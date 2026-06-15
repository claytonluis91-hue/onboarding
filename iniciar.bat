@echo off
title Portal Fiscal e Contabil - Nascel
echo ===================================================
echo Verificando e instalando dependencias (se necessario)...
echo ===================================================
python -m pip install streamlit requests pandas fpdf2
echo.
echo ===================================================
echo Iniciando o Portal Fiscal e Contabil (Streamlit)...
echo ===================================================
echo.
python -m streamlit run app.py
pause
