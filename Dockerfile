# Based on https://github.com/mdirkse/rust_armv6
# We use bullseye to match glibc versions with raspios old stable
FROM --platform=linux/amd64 rust:slim-bullseye

# Prevent any error messages about there not being a terminal
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qq && \
    # Install the necessary packages to build & cross compile
    apt-get install -qq --no-install-recommends pkg-config libc6-dev-armhf-cross gcc-arm-linux-gnueabihf libc6-dev-arm64-cross gcc-aarch64-linux-gnu libc6-dev-arm64-cross && \
    # Purge anything that has become useless
    apt-get autoremove -qq --purge && \
    # And finally do cleanup
    apt-get clean -qq && rm -fr /var/lib/apt/* /var/cache/apt/*

# Enable arm v6 and aarch64 in Rust
RUN rustup target add arm-unknown-linux-gnueabihf
RUN rustup target add aarch64-unknown-linux-gnu

CMD PKG_CONFIG_PATH=/usr/lib/arm-linux-gnueabihf/pkgconfig cargo build --release --target=arm-unknown-linux-gnueabihf && \
    PKG_CONFIG_PATH=/usr/libaarch64-linux-gnu/pkgconfig cargo build --release --target=aarch64-unknown-linux-gnu
