# Based on https://github.com/mdirkse/rust_armv6
# We use buster to match glibc versions with raspios old stable
FROM rust:slim-buster

# Prevent any error messages about there not being a terminal
ENV DEBIAN_FRONTEND noninteractive
# Allow pkg-config to find 
ENV PKG_CONFIG_PATH=/usr/lib/arm-linux-gnueabihf/pkgconfig
# RPI tools dir
ENV RPI_TOOLS=/rpi_tools

# Enable the armhf arch
RUN dpkg --add-architecture armhf
RUN apt-get update -qq && \
    # Install the necessary packages
    # libudev-dev will also bring in the arm libc6 and gcc packages
    apt-get install -qq --no-install-recommends git pkg-config libudev-dev:armhf && \
    # Add the RPI toolchain
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

# Enable arm v6 in Rust
RUN rustup target add arm-unknown-linux-gnueabihf

CMD cargo build --release --target=arm-unknown-linux-gnueabihf
# CMD /rpi_tools/arm-bcm2708/arm-linux-gnueabihf/bin/arm-linux-gnueabihf-gcc -v
