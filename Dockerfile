# Based on https://github.com/mdirkse/rust_armv6
# We use buster to match glibc versions with raspios old stable
FROM rust:slim-buster

# Prevent any error messages about there not being a terminal
ENV DEBIAN_FRONTEND noninteractive

# Bring in armhf compiler
RUN apt-get update -qq && apt install -y gcc-arm-linux-gnueabihf

# Enable arm v6 in Rust
RUN rustup target add arm-unknown-linux-gnueabihf

# CMD cargo build --release --target=arm-unknown-linux-gnueabihf
CMD arm-linux-gnueabihf-gcc -v
