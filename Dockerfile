# Based on https://github.com/mdirkse/rust_armv6
# We use bookworm to match glibc versions with raspios old stable
FROM --platform=linux/amd64 rust:slim-bookworm

# Prevent any error messages about there not being a terminal
ENV DEBIAN_FRONTEND noninteractive
# RPI tools dir
ENV RPI_TOOLS=/rpi_tools

RUN apt-get update -qq && \
    # Install the necessary packages to build & cross compile
    apt-get install -qq --no-install-recommends git pkg-config libc6-dev-armhf-cross gcc-arm-linux-gnueabihf libc6-dev-arm64-cross gcc-aarch64-linux-gnu libc6-dev-arm64-cross && \
    # Add the RPI arm v6 toolchain
    git -C "/" clone -q --depth=1 https://github.com/raspberrypi/tools.git "${RPI_TOOLS}" && \
    # Remove most of the repo we just downloaded as we only need a small amount
    rm -fr "${RPI_TOOLS}/.git" \
           "${RPI_TOOLS}/arm-bcm2708/arm-bcm2708-linux-gnueabi" \
           "${RPI_TOOLS}/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi" \
           "${RPI_TOOLS}/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian" \
           "${RPI_TOOLS}/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64" && \
    # Then get rid of git as we only needed it to fetch the rpi tools
    apt-get purge -qq git && \
    # Purge anything that has become useless
    apt-get autoremove -qq --purge && \
    # And finally do cleanup
    apt-get clean -qq && rm -fr /var/lib/apt/* /var/cache/apt/*

# Enable arm v6 and aarch64 in Rust
RUN rustup target add arm-unknown-linux-gnueabihf
RUN rustup target add aarch64-unknown-linux-gnu

CMD PKG_CONFIG_PATH=/usr/lib/arm-linux-gnueabihf/pkgconfig cargo build --release --target=arm-unknown-linux-gnueabihf && \
    PKG_CONFIG_PATH=/usr/lib/aarch64-linux-gnu/pkgconfig cargo build --release --target=aarch64-unknown-linux-gnu
