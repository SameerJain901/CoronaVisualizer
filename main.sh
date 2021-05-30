chmod 755 .streamlit/config.toml

echo "\
[general]\n\
email = \”sameerjain901@gmail.com\”\n\
" > ~/.streamlit/credentials.toml

echo "[server]
headless = true
port = 8501
enableCORS = false
" > ~/.streamlit/config.toml

