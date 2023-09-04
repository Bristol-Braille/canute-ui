docker build --pull -t bristol-braille/bookindex:latest .

docker run --rm -t -u "$(id -u):$(id -g)" -e "HOME=/work" -w /work -v "$(pwd):/work" -v "${HOME}/.cargo/registry:/usr/local/cargo/registry" bristol-braille/bookindex:latest
