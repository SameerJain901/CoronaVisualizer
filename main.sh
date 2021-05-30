chmod 755 ~/.streamlit/config.toml
chmod 755 ~/.streamlit

echo "\
[general]\n\
email = \”sameerjain901@gmail.com\”\n\
" > ~/.streamlit/credentials.toml

echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml

